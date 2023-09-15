# SPDX-FileCopyrightText: 2018 - 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, yaml
from subprocess import run, Popen, PIPE

from fdbuild import utils
from fdbuild import config as cfg
from fdbuild.exceptions import StructurizeError
from fdbuild.settings import Settings


class Project:
    def __init__(self, path):
        self.name = ""
        self.identifier = ""
        self.repopath = ""
        self.metadata_path = path
        self.dependencies = set()
        self.anti_dependencies = set()
        self.meta_package = False

    def __repr__(self):
        return "<" + self.name + ">"

    def __str__(self):
        return "<Project object " + self.identifier + ">"

    def add_dependency(self, identifier):
        self.dependencies.add(identifier)

    def add_anti_dependency(self, identifier):
        self.anti_dependencies.add(identifier)

    def set_metadata(self, root_path):
        full_path = os.path.join(root_path, self.metadata_path, "metadata.yaml")

        try:
            with open(full_path, "r") as file:
                metadata = yaml.safe_load(file)
        except:
            print("Error: could not read metadata from file:", full_path)
            raise

        self.name = metadata["name"]
        self.identifier = metadata["identifier"]
        self.path = metadata["projectpath"]
        self.repopath = metadata["repopath"]


# TODO: not really needed, right? can use the Project class as well.
class MetaPackage:
    def __init__(self, path):
        self.name = ""
        self.path = path
        self.dependencies = set()

    def __repr__(self):
        return "<" + self.path + ">"

    def __str__(self):
        return "<MetaPackage object " + self.name + " in " + self.path + ">"

    def add_dependency(self, identifier):
        self.name = identifier
        self.dependencies.add(identifier)


class Plugin:
    def __init__(self, structurizer):
        self.settgs = structurizer.settgs

        helpers_path = os.path.join(structurizer.path(), ".fdbuild", "structure", "kde")
        self.repo_meta_path = os.path.join(helpers_path, "repo-metadata")

        # Default values
        self.branch_group = "kf6-qt6"
        self.flat = True
        self.selection_settgs = set(["frameworks"])
        self.git_origin_update = False

        self.repo_index = {}

        self.projects = {}
        self.meta_packages = {}

        self.selected_projects = {}

        self.dependency_chain = None
        self.projects_chain = []

        self.projects_map = {}

    def acquire_helper_repos(self):
        self.log.print("Aquiring helper repos.")

        def init_helper_src(src_path, origin):
            utils.make_dir(src_path)

            if os.path.isdir(os.path.join(src_path, ".git")):
                cmd = ["git", "-C", src_path, "pull", "--rebase"]
            else:
                cmd = ["git", "clone", origin, src_path]

            p1 = run(cmd, stdout=PIPE, stderr=PIPE)
            self.log.out(p1.stdout)
            self.log.err(p1.stderr)

        init_helper_src(self.repo_meta_path, "https://invent.kde.org/sysadmin/repo-metadata.git")

    def init_repo_index(self):
        """Reads in the repo index file and caches the json data as a simple map."""
        self.log.print("Reading repo index file.")

        back_dir = os.getcwd()
        os.chdir(self.repo_meta_path)

        for root, dirs, files in os.walk("projects"):
            for name in files:
                if name == "metadata.yaml":
                    path = os.path.join(root, name)
                    self.repo_index[root] = root

    def init_projects(self):
        """Initializes the set of all projects and the special case of the kfumbrella meta-package.
        We actually use the path instead of the name as key for our map since it fits with
        how the dependency file is written. Entries are one-to-one."""
        umbrella_project = Project("frameworks/kfumbrella")
        umbrella_project.name = "kfumbrella"
        umbrella_project.path = "frameworks/kfumbrella"
        self.projects["frameworks/kfumbrella"] = umbrella_project

        for name, path in self.repo_index.items():
            project = Project(path)
            project.set_metadata(self.repo_meta_path)
            self.projects[project.path] = project

    def init_dependencies(self):
        """Initializes all dependencies"""
        dependency_file_path = os.path.join(
            self.repo_meta_path, "dependencies", "dependency-data-" + self.branch_group
        )
        with open(dependency_file_path, "r") as dependency_file:
            dependency_lines = [
                line.strip()
                for line in dependency_file.readlines()
                if line[0] != "#" and line.isspace() == False
            ]

        meta_packages = {}

        for d_line in dependency_lines:
            # Remove comments first.
            d_line = d_line.split("#")[0]
            if not d_line:
                # Was just a comment or an empty line to begin with.
                continue

            [dependent, dependency] = map(str.strip, d_line.split(":"))

            ## Ignore Qt5 and other third-party stuff, we don't handle it in here.
            if "third-party/" in d_line:
                continue

            if dependent[-1] == "*":
                # Generic dependency. Will be handled as a meta package.
                if dependent in meta_packages:
                    meta_packages[dependent].add_dependency(dependency)
                else:
                    meta_package = MetaPackage(dependent[:-1])
                    meta_package.add_dependency(dependency)
                    meta_packages[dependent] = meta_package
                continue

            if not any(project.path == dependent for key, project in self.projects.items()):
                # We don't care about third-party projects and so on.
                continue

            if dependency[0] == "-":
                # That is an anti-dependency.
                self.projects[dependent].add_anti_dependency(dependency[1:])
            else:
                # Normal dependency to add.
                self.projects[dependent].add_dependency(dependency)

        def transfer_dependencies(project, meta_package):
            if not project.path.startswith(meta_package.path):
                # Project is not part of this meta package.
                return
            if project.path in meta_package.dependencies:
                # Project is the meta-package. Do not add dependency on itself.
                return
            # This project is part of the meta package. Copy all dependencies over.
            for dependency in meta_package.dependencies:
                if dependency in project.anti_dependencies:
                    # Project explicitly excluded this dependency. Ignore it.
                    continue
                project.dependencies.add(dependency)

        # Now we transform the temporary meta_packages into actual dependencies per project.
        for key in meta_packages:
            for path, project in self.projects.items():
                transfer_dependencies(project, meta_packages[key])

    def deconstruct_dependencies(self):
        """Use tsort to build a linear dependency chain."""

        tsort_input = ""
        for path, project in self.projects.items():
            for dependency in project.dependencies:
                tsort_input += project.path + " " + dependency + " "

        tsort_byte_input = str.encode(tsort_input)

        with Popen(
            [
                "tsort",
            ],
            stdout=PIPE,
            stdin=PIPE,
        ) as tsort:
            tsort_output = tsort.communicate(input=tsort_byte_input)[0]

        if tsort.returncode != 0:
            raise StructurizeError("kde")  # TODO: add log

        self.dependency_chain = tsort_output.decode().split("\n")

    def filter_dependency_chain(self):
        """Filters dependencies such that in the end only projects are in it"""
        self.dependency_chain = [dep for dep in self.dependency_chain if dep in self.projects]

    def get_selection(self):
        """What selection of projects did the user choose."""
        selection = self.settgs.read(["structure", "selection"])

        # TODO: Do this for branch_group as well
        if isinstance(selection, str):
            self.selection_settgs = set([selection])
        elif isinstance(selection, list):
            self.selection_settgs = set(selection)
        elif selection:
            raise

        selection = set(self.selection_settgs)
        generic_selectors = set()

        def generic_select(path, project):
            for selector in selection:
                if project.path.startswith(selector):
                    if project.path[len(selector)] == "/" or selector[-1] == "/":
                        # Do not remove the generic selection for other projects.
                        generic_selectors.add(selector)
                        self.selected_projects[path] = project
                        return

        for path, project in self.projects.items():

            def exact_select(key):
                if not key in selection:
                    return False
                selection.remove(key)
                self.selected_projects[path] = project
                return True

            if exact_select(project.identifier):
                continue
            if exact_select(project.repopath):
                continue
            if exact_select(project.path):
                continue

            # See if this is part of a generic selection.
            generic_select(path, project)

        if selection:
            for selector in selection:
                if selector in generic_selectors:
                    # Generic selectors are still in the list. That's fine.
                    continue
                # A project was selected that was not found. Raise an error.
                # TODO: add log and name the not-found projects there
                raise StructurizeError("kde", None, "Selected projects not found.")

    def select_projects_and_dependencies(self):
        """This filters the dependency chain such that only selected projects and
        their dependencies are included."""
        dependency_chain = []

        # We go through the dependency chain and wait for the first occurence of a selection.
        # Every entry afterwards is selected implicitly as a dependency.
        for count, project_identifier in enumerate(self.dependency_chain):
            if not project_identifier in self.selected_projects:
                continue
            # We found the first selected entry. We don't need the rest of the dependency
            # chain anymore. So just cut it off here.
            dependency_chain = self.dependency_chain[count:]
            # Copy it back:
            self.dependency_chain = list(dependency_chain)
            break

        # Insert first the selected projects to have a starting point for every
        # potential separate sub-chain.
        i = 0
        while i < len(dependency_chain):
            identifier = dependency_chain[i]
            if identifier in self.selected_projects:
                self.projects_chain.append(self.selected_projects[identifier])
                dependency_chain.pop(i)
            else:
                i = i + 1

        while True:
            found_new_dependency = False
            for i, identifier in enumerate(dependency_chain):
                for project in self.projects_chain:
                    if identifier in project.dependencies:
                        self.projects_chain.append(self.projects[identifier])
                        # We can just pop it here because we break out of the loop afterwards.
                        dependency_chain.pop(i)
                        found_new_dependency = True
                        break
                if found_new_dependency:
                    break
            if not found_new_dependency:
                break

        # Now reverse the chains such that the first element in the list is the first to be built.
        self.dependency_chain.reverse()
        self.projects_chain.reverse()

        # tsort earlier produced the dependency chain. But it is not unique. It is only a
        # partial ordering. And tsort manages to output different results each time. But to
        # get a unique result let's reorder projects without dependency lexicographically.
        projects_work = []

        # For that we remember for every projects its dependents.
        for i, project in enumerate(self.projects_chain):
            project_struct = {"project": project, "dependents": []}
            j = i + 1

            while j < len(self.projects_chain):
                dependent = self.projects_chain[j]
                if project.path in dependent.dependencies:
                    project_struct["dependents"].append(dependent)
                j = j + 1

            projects_work.append(project_struct)

        # Then we build subsets of projects that don't have dependents, order these
        # lexicographically, add them to the result and make the remaining list to work on
        # independent of them. This way a new subset of projects without dependents can be
        # identified and the method reapplied until all projects have been prepended into
        # the resulting sorted list.
        sorted_projects = []
        while len(projects_work):
            projects_without_dependents = []

            for p in reversed(projects_work):
                if not p["dependents"]:
                    projects_without_dependents.append(p["project"])
                    projects_work.remove(p)

            assert projects_without_dependents
            projects_without_dependents.sort(key=lambda project: project.path)
            sorted_projects = projects_without_dependents + sorted_projects

            # Now remove the dependents from other projects (by that at least one
            # other project should have no dependents anymore).
            for p in projects_work:
                for dependent in reversed(p["dependents"]):
                    for q in projects_without_dependents:
                        if dependent.path == q.path:
                            p["dependents"].remove(dependent)
                            break

        self.projects_chain = sorted_projects

        # Remove the kfumbrella substitute now again. It is not needed anymore
        # and must be kept from creeping into any final output.
        kfumbrella_identifier = "frameworks/kfumbrella"
        kfumbrella_project = self.projects.pop(kfumbrella_identifier)
        if kfumbrella_project in self.projects_chain:
            self.projects_chain.remove(kfumbrella_project)
        for project in self.projects_chain:
            if kfumbrella_identifier in project.dependencies:
                project.dependencies.remove(kfumbrella_identifier)
            assert kfumbrella_identifier not in project.dependencies

        self.log.print("\nStructure with the following projects:")
        for project in self.projects_chain:
            self.log.print(project.name)

    def get_direct_dependency_link(self, project, dependency):
        """Get a dependency that is not covered by the directory structure"""
        # Can only happen when we don't build a flat structure. Otherwise all projects
        # are built as is the dependency chain.
        assert not self.flat
        assert project.path != dependency

        project_path = project.path.split("/")
        dependency_path = dependency.split("/")

        while project_path[0] == dependency_path[0]:
            project_path.pop(0)
            dependency_path.pop(0)

        updir_count = len(project_path)
        return updir_count * [".."] + dependency_path

    def build_projects_map(self):
        """Builds a projects map according to flat or stacked file system structure."""

        current_identifier = ""

        def get_final_project_settings(project_name, path):
            """Gets leaf settings in the structure."""
            project = self.projects[current_identifier]

            remote_path = "https://invent.kde.org/" + project.repopath + ".git"
            project_settings = {"source": {"origin": remote_path}}

            return project_settings

        def add_projects_entry(dictionary, path, subproject_identifier):
            """Adds subproject entry to dictionary and returns the modified one.
            Keyword arguments:
            dictionary ---
            subproject_identifier --- the name of the subproject as a string
            """
            if "projects" not in dictionary:
                dictionary["projects"] = []

            for i, project in enumerate(dictionary["projects"]):
                if project[0] == subproject_identifier:
                    return i

            project_entry = [subproject_identifier, {}]
            dictionary["projects"].append(project_entry)

            return len(dictionary["projects"]) - 1

        def append_project_recursive(prev_dictionary, prev_path, remaining_path):
            """Recursion step to append a project defined by prev_path and remaining_path. In this
            step the next part of remaining_path is worked on.
            Keyword arguments:
            prev_dictionary --- the previous dictionary one level up we amend with more information
            it must have already added an entry for this project in its projects entry that we can
            then use.
            prev_path --- the path until now
            remaining_path --- the path we still need to recurse including the current step.
            """

            def add_project_dictionary_to_prev_dictionary(position, subproject, dictionary):
                prev_dictionary["projects"][position][0] = subproject
                prev_dictionary["projects"][position][1] = dictionary

            subproject_identifier = remaining_path.pop(0)
            current_path = prev_path + [subproject_identifier]

            position = add_projects_entry(
                prev_dictionary, ("/").join(current_path), subproject_identifier
            )
            current_dictionary = prev_dictionary["projects"][position][1]

            if not remaining_path:
                # This was the last level of recursion and next_path is the project identifier itself.
                current_dictionary = get_final_project_settings(subproject_identifier, current_path)
                add_project_dictionary_to_prev_dictionary(
                    position, subproject_identifier, current_dictionary
                )
                return

            append_project_recursive(current_dictionary, current_path, remaining_path)

        # We start with the top-level where the structure was defined.
        self.projects_map = {}

        # We build our file-system view now, the final structure. First element to build is the dependency most are dependent on.
        for project in self.projects_chain:
            current_identifier = project.path
            path = [project.identifier] if self.flat else project.path.split("/")
            append_project_recursive(self.projects_map, [], path)

        # We add direct dependencies for project not being built according to the directory structure.
        prev_identifiers = []

        def get_direct_dependencies(project):
            dependencies = []
            for dependency in project.dependencies:
                if dependency not in prev_identifiers and dependency in self.dependency_chain:
                    # Add an out of order dependency.
                    link = self.get_direct_dependency_link(project, dependency)
                    dependencies.append((dependency, link))

            # Sort the dependencies according to our dependency chain. This also filters projects
            dependencies_sorted = []
            if dependencies:
                for dependency in self.dependency_chain:
                    for dep_tuple in dependencies:
                        if dependency == dep_tuple[0]:
                            dependencies_sorted.append("/".join(dep_tuple[1]))
                            break
            return dependencies_sorted

        def add_direct_dependencies(subproject, path):
            subproject_name = subproject[0]
            data = subproject[1]

            next_path = path + [subproject_name]

            if "projects" not in data:
                # Final level.
                identifier = "/".join(next_path)
                project = self.projects[identifier]
                prev_identifiers.append(identifier)
                dependencies = get_direct_dependencies(project)
                if dependencies:
                    data["depends"] = dependencies
            else:
                for project in data["projects"]:
                    add_direct_dependencies(project, next_path)

        if not self.flat:
            # Direct dependencies are only relevant in non-flat structure. Otherwise we just
            # build in one after the other in the dependency chain.
            for project in self.projects_map["projects"]:
                add_direct_dependencies(project, [])

        def merge_projects_settings(list1, list2):
            # The items in dic1 are two-elements lists, the identifier is the first element.
            for e2 in reversed(list2):
                if all(e1[0] != e2 for e1 in list1):
                    list1.insert(0, [e2, {}])

        def merge_dics(dic1, dic2):
            """Merges dictionary dic2 into dictionary dic1 without overriding values. Useful for settings"""
            for key, value in dic2.items():
                if key not in dic1:
                    dic1[key] = value

                elif isinstance(value, dict):
                    assert isinstance(dic1[key], dict)
                    merge_dics(dic1[key], value)

                elif isinstance(value, list):
                    assert isinstance(dic1[key], list)
                    if key == "projects":
                        merge_projects_settings(dic1[key], value)
                    else:
                        for element in reversed(value):
                            if element not in dic1[key]:
                                dic1[key].insert(0, element)

        def get_settings(path):
            sub_path = ("/").join(path)
            settings_path = os.path.join(
                os.path.dirname(self.settgs.path), sub_path, cfg.SETTGS_NAME
            )
            return Settings(settings_path, None).data

        def merge_settings(project, prev_path):
            path = prev_path + [project[0]]

            has_subprojects = "projects" in project[1]
            if has_subprojects:
                # Recurse further.
                for subproject in project[1]["projects"]:
                    merge_settings(subproject, path)

            # Now merge own settings.
            settings = get_settings(path)
            merge_dics(project[1], settings)

            if not has_subprojects and "projects" in project[1]:
                # Final level. The projects field may not be merged, otherwise we can't work on the level.
                raise StructurizeError("kde")  # TODO: add log

        # Now we merge all current settings into our structure.
        # Begin with all subprojects.
        for project in self.projects_map["projects"]:
            merge_settings(project, [])

        # In the end don't forget to merge the top-level.
        settings = get_settings([])
        merge_dics(self.projects_map, settings)

    def set_default_settings(self):
        """Sets the necessary settings for a typical KDE build if not already set in some
        settings file in the projects hierarchy."""

        # We get structure settings only without hierarchy lookup. Therefore always set them.
        settings = {}
        if "structure" in self.projects_map:
            settings = self.projects_map["structure"]

        settings["branch-group"] = self.branch_group
        self.projects_map["structure"] = settings

        def correct_settings(settings):
            if isinstance(settings, dict):
                return settings
            return {}

        parent_settgs = self.settgs.get_adhoc_parent()

        def add_value(key1, key2, val, override_parent=True):
            # Read in the settings in the current file (including other settings not added here).
            settings = correct_settings(self.settgs.read([key1], hierarchy_lookup=False))

            def set_value():
                if key2 in settings:
                    # Only set value if not explicitly overridden already in this settings file.
                    return False

                if parent_settgs:
                    parent_val = parent_settgs.read([key1, key2])
                    if parent_val != None:
                        # If we have a parent value which is the same or we should always use it abort.
                        if parent_val == val or not override_parent:
                            return False

                settings[key2] = val
                return True

            has_value_set = set_value()

            if len(settings):
                if key1 not in self.projects_map:
                    # If we haven't yet added the key to the projects map we need to do that for
                    # potentially other unprocessed values.
                    self.projects_map[key1] = settings
                elif key2 in settings:
                    # If the value is still in settings, add it now.
                    self.projects_map[key1][key2] = settings[key2]
            if key1 in self.projects_map and len(self.projects_map[key1]) == 0:
                # If we removed all values from the map at key1, remove the map itself.
                del self.projects_map[key1]

            return has_value_set

        add_value("source", "plugin", "git")
        add_value("configure", "plugin", "cmake")
        add_value("build", "plugin", "ninja")
        add_value("build", "threads", "max", override_parent=False)
        if add_value("install", "path", "/usr/local", override_parent=False):
            add_value("install", "sudo", False, override_parent=False)

    def prepare(self):
        is_flat = self.settgs.read(["structure", "flat"])
        if is_flat is not None:
            self.flat = is_flat

        branch_group = self.settgs.read(["structure", "branch-group"])
        if branch_group:
            self.branch_group = branch_group

        git_origin_update = self.settgs.read(["structure", "git origin update"])
        if git_origin_update:
            self.git_origin_update = git_origin_update

    def project_post_hook(self, path, structure):
        if not self.git_origin_update:
            return
        if not "source" in structure:
            return

        if not os.path.isdir(os.path.join(path, "src", ".git")):
            return

        back_dir = os.getcwd()
        os.chdir(os.path.join(path, "src"))

        cmd = ["git", "remote", "set-url", "origin", structure["source"]["origin"]]
        p1 = run(cmd, stdout=PIPE, stderr=PIPE)
        if p1.returncode != 0:
            raise StructurizeError("kde")  # TODO: add log

        os.chdir(back_dir)

    def structure(self, log):
        self.log = log
        self.prepare()

        self.acquire_helper_repos()

        self.init_repo_index()
        self.init_projects()

        self.init_dependencies()
        self.deconstruct_dependencies()
        self.filter_dependency_chain()

        self.get_selection()
        self.select_projects_and_dependencies()

        self.build_projects_map()

        self.set_default_settings()

        return self.projects_map
