import datetime
from distutils.dir_util import copy_tree
import filecmp
from fileinput import filename
import os
from os.path import dirname
import pathlib
from pathlib import Path
import random
import shutil
import sys
from tkinter.constants import N

import matplotlib.pyplot as plt
import networkx as nx


ROOT_ID = "ROOT"
current_folder = os.getcwd()
current_folder = Path(current_folder)


def start():
    cmd_line_list = sys.argv
    if len(sys.argv) == 1:
        print("Waiting for instructions")
    if len(sys.argv) > 1:
        if cmd_line_list[1] == "init":
            init()
        if cmd_line_list[1] == 'status':
            status(cmd_line_list)
        if cmd_line_list[1] == 'graph':
            graph(cmd_line_list)
    if len(sys.argv) > 2:
        if cmd_line_list[1] == 'add':
            add(cmd_line_list[2])
        if cmd_line_list[1] == 'commit':
            commit(cmd_line_list)
        if cmd_line_list[1] == 'checkout':
            checkout(cmd_line_list)
        if cmd_line_list[1] == 'branch':
            branch(cmd_line_list)
        if cmd_line_list[1] == 'merge':
            merge(cmd_line_list)


def parent_list(hash, closest_wit):
    list_of_commits = []
    while hash != ROOT_ID:
        parent = find_parent(hash, closest_wit)
        list_of_commits.append(parent)
        hash = parent
    if list_of_commits == [ROOT_ID]:
        print("you are your parent")
    else:
        return list_of_commits


def compare_folder_diff(closest_wit, hash1, hash2):
    hash1_image_folder = closest_wit / "images" / hash1
    hash2_image_folder = closest_wit / "images" / hash2
    dcmp = filecmp.dircmp(hash1_image_folder, hash2_image_folder)
    return dcmp.diff_files


def find_younger_parent(requested_branch_parents, active_parents):
    common = [a for a in requested_branch_parents if a in active_parents]
    return common[0]


def find_common_parent(HEAD_id, requested_branch_id, closest_wit, lines_in_file):
    if HEAD_id == requested_branch_id:
        return requested_branch_id
    else:
        requested_branch_parents = parent_list(
            requested_branch_id, closest_wit)
        active_parents = parent_list(HEAD_id, closest_wit)
        younger_parent = find_younger_parent(
            requested_branch_parents, active_parents)
        return younger_parent


def merge(cmd_line_list):
    requested_branch_id = None
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    else:
        branch_name = cmd_line_list[2]
        reference_file = closest_wit / "references.txt"
        with open(reference_file, "r") as rf_name:
            lines_in_file = rf_name.readlines()
            for line in lines_in_file:
                if line.startswith("HEAD="):
                    HEAD_id = ((line.split("="))[1]).strip("\n")
                if line.startswith(branch_name):
                    requested_branch_id = ((line.split("="))[1]).strip("\n")
        if requested_branch_id is None:
            print('no such branch')
        else:
            common_parent = find_common_parent(
                HEAD_id, requested_branch_id, closest_wit, lines_in_file)
            print("common parent found")
            compare_folder_diff(
                closest_wit, common_parent, requested_branch_id)
            update_staging_area(common_parent, closest_wit)
            message = f"Merger between {HEAD_id} and {requested_branch_id}"
            id_file_name, parent, print_now = commit(message)
            update_commit_text(id_file_name, parent,
                               requested_branch_id, print_now, message)


def update_commit_text(id_file_name, parent, requested_branch_id, print_now, message):
    id_file_info = (
        f"parent={parent}, {requested_branch_id}\n{print_now}\nmessage={message}")
    with open(id_file_name, "w") as id_file:
        id_file.writelines(id_file_info)


def branch(cmd_line_list):
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    else:
        branch_name = cmd_line_list[2]
        if check_ref_file(closest_wit):
            reference_file = closest_wit / "references.txt"
            if check_if_branch_exists(closest_wit, branch_name):
                print("There is a branch by that name. Hire a copywriter ASAP")
            else:
                print(f"Creating {branch_name} branch...")
                with open(reference_file, "r") as rf_name:
                    lines_in_file = rf_name.readlines()
                    for line in lines_in_file:
                        if line.startswith("HEAD="):
                            HEAD = line[5:]
                            print(HEAD)
                        if line.startswith("master="):
                            master = line[7:]
                            print(master)
                with open(reference_file, "a") as rf_name:
                    rf_name.writelines(f"{branch_name}={HEAD}")


def graph(cmd_line_list):
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    else:
        g = nx.Graph()
        g = g.to_directed()
        reference_file = closest_wit / "references.txt"
        if os.path.isfile(reference_file):
            with open(reference_file, "r") as rf_name:
                lines_in_file = rf_name.readlines()
                for line in lines_in_file:
                    splitted_line = line.split("=")
                    branch_name = splitted_line[0]
                    branch_id = splitted_line[1].strip("\n")
                    g.add_edge(branch_name[:7], branch_id[:7])
                    parents = parent_list(branch_id, closest_wit)
                    g.add_edge(branch_id[:7], parents[0][:7])
                    for i in range(len(parents)-1):
                        g.add_edge(parents[i][:7], parents[i+1][:7])
        nx.draw_networkx(g, node_size=2500, alpha=0.8)
        plt.show()


def find_parent(master_id, closest_wit):
    id_file_name = closest_wit / "images" / master_id
    id_file_name = str(id_file_name) + ".txt"
    with open(id_file_name, "r") as id_name:
        lines_in_file = id_name.readlines()
        for line in lines_in_file:
            if line.startswith("parent="):
                parent = line[7:-1]
                return parent


def find_master(closest_wit):
    reference_file = closest_wit / "references.txt"
    if os.path.isfile(reference_file):
        print("Searching Master...")
        with open(reference_file, "r") as rf_name:
            lines_in_file = rf_name.readlines()
            for line in lines_in_file:
                if line.startswith("master="):
                    master_id = line[7:-1]
                    return master_id


def check_if_branch_exists(closest_wit, branch_name):
    reference_file = closest_wit / "references.txt"
    if os.path.isfile(reference_file):
        with open(reference_file, "r") as rf_name:
            lines_in_file = rf_name.readlines()
            for line in lines_in_file:
                if line.startswith(branch_name):
                    return True


def check_activeted_file(closest_wit):
    activated_file = closest_wit / "activated.txt"
    with open(activated_file, "r") as ac_file:
        return ac_file.readline()


def update_activeted_file(closest_wit, active_branch):
    activated_file = closest_wit / "activated.txt"
    print("updatind activated file...")
    with open(activated_file, "w") as ac_file:
        ac_file.writelines(active_branch)


def rollback_folder(commit_id_image_folder, closest_wit):
    print("Rollback")
    for dirpath, _dirnames, filenames in os.walk(commit_id_image_folder, topdown=False):
        for filename in filenames:
            file_to_rollback = os.path.join(dirpath, filename)
            closest_wit_tree = str(closest_wit)
            closest_wit_tree = closest_wit_tree[:-4]
            closest_wit_tree = Path(closest_wit_tree)
            str_img_folder = str(commit_id_image_folder)
            sub_path_to_rollback = file_to_rollback[len(str_img_folder):]
            rollback_path = os.path.join(
                closest_wit_tree, sub_path_to_rollback[1:])
            shutil.copy(file_to_rollback, rollback_path)


def update_staging_area(commit_id_image_folder, closest_wit):
    staging_area = closest_wit / "staging_area"
    for dirpath, _dirnames, filenames in os.walk(commit_id_image_folder, topdown=False):
        for filename in filenames:
            file_to_rollback = os.path.join(dirpath, filename)
            staging_area_tree = str(staging_area)
            str_img_folder = str(commit_id_image_folder)
            sub_path_to_rollback = file_to_rollback[len(str_img_folder):]
            rollback_path = os.path.join(
                staging_area_tree, sub_path_to_rollback[1:])
            shutil.copy(file_to_rollback, rollback_path)
    print("staging area updated")


def checkout(cmd_line_list):
    branch_name = None
    current_commit_id = cmd_line_list[2]
    closest_wit = find_closest_wit(current_folder)
    reference_file = closest_wit / "references.txt"
    current_branch = check_activeted_file(closest_wit)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
        return
    if check_ref_file(closest_wit):
        reference_file = closest_wit / "references.txt"
        with open(reference_file, "r") as rf_name:
            lines_in_file = rf_name.readlines()
            for line in lines_in_file:
                split_line = line.split("=")
                if current_commit_id in split_line:
                    branch_name = split_line[0]
                    current_commit_id = split_line[1]
                    current_commit_id = current_commit_id.strip("\n")

    commit_id_image_folder = closest_wit / "images" / current_commit_id
    if os.path.isdir(commit_id_image_folder):
        dcmp_original, dcmp_image = folder_diff(current_commit_id)
        print('Changes to be committed      :', dcmp_image.left_only)
        print('Changes not staged for commit:', dcmp_original.diff_files)
        print('Untracked files:             :', dcmp_original.right_only)
        if len(dcmp_image.left_only) or len(dcmp_original.diff_files) > 0:
            print("As my mamma said: 'You need to commit first'")
            return

    if branch_name is not None:
        if branch_name == current_branch:
            rollback_folder(commit_id_image_folder, closest_wit)
            print("all files restored")
            update_staging_area(commit_id_image_folder, closest_wit)
        if check_ref_file(closest_wit):
            with open(reference_file, "r") as rf_name:
                lines_in_file = rf_name.readlines()
                for line in lines_in_file:
                    if line.startswith(cmd_line_list[2]):
                        update_activeted_file(closest_wit, branch_name)
        else:
            print(f"{current_commit_id} is not a real backup. nice try.")


def folder_diff(current_commit_id):
    closest_wit = find_closest_wit(current_folder)
    if current_commit_id == "MASTER":
        print("Master")
    else:
        commit_id_image_folder = closest_wit / "images" / current_commit_id
        staging_area = closest_wit / "staging_area"
        dcmp_original = filecmp.dircmp(staging_area, current_folder)
        dcmp_image = filecmp.dircmp(staging_area, commit_id_image_folder)
        return dcmp_original, dcmp_image


def status(cmd_line_list):
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    elif find_closest_wit(current_folder):
        reference_file = closest_wit / "references.txt"
        with open(reference_file, "r") as rf_name:
            lines_in_file = rf_name.readlines()
            for line in lines_in_file:
                if line.startswith("HEAD="):
                    current_commit_id = line[5:-1]
                    print(f"Current commit ID is: {current_commit_id}")
                    dcmp_original, dcmp_image = folder_diff(current_commit_id)
                    print('Changes to be committed      :', dcmp_image.left_only)
                    print('Changes not staged for commit:',
                          dcmp_original.diff_files)
                    print('Untracked files:             :',
                          dcmp_original.right_only)


def write_ref_file(closest_wit, current_commit_id):
    if check_ref_file(closest_wit):
        reference_file = closest_wit / "references.txt"
        if os.path.isfile(reference_file):
            print("updating reference file...")
            with open(reference_file, "r") as rf_name:
                lines_in_file = rf_name.readlines()
                for line in lines_in_file:
                    if line.startswith("HEAD="):
                        old_commit_id = line[5:]
                        print(old_commit_id)
                        print(current_commit_id)
        with open(reference_file, "w") as rf_name:
            rf_name.writelines(
                f"HEAD={current_commit_id}\nmaster={old_commit_id}\n")


def commit(cmd_line_list):
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. Please backup soon...")
        return

    reference_file = closest_wit / "references.txt"
    if not os.path.isfile(reference_file):
        print("Creating new reference file")
        with open(reference_file, "w") as rf_name:
            rf_name.writelines(f"HEAD={ROOT_ID}\nmaster={ROOT_ID}\n")
        create_activated_file(closest_wit)
    current_branch = check_activeted_file(closest_wit)
    if os.path.isfile(reference_file):
        print("Checking old reference")
        with open(reference_file, "r") as rf_name:
            lines_in_file = rf_name.readlines()
            for line in lines_in_file:
                if line.startswith("HEAD="):
                    head_id = line.split("=")[1]
                    parent = head_id
                if line.startswith(current_branch):
                    active_id = line.split("=")[1]
    if head_id != active_id:
        print("HEAD is Decapitated")
        return
    commit_id, images_folder, commit_id_image_folder = create_commit_id()
    if os.path.isdir(commit_id_image_folder):
        print("You've randomed twice... fill the lottory now!")
        return

    os.makedirs(commit_id_image_folder)
    now = datetime.datetime.now()
    print_now = now.strftime("%A %b %d %H:%M:%S %Y %z")
    if os.path.isfile(reference_file):
        print("Addind to old reference")
        with open(reference_file, "r") as rf_name:
            file_content = rf_name.readlines()
            for i, line in enumerate(file_content):
                name = line.split("=")[0]
                if name in ["HEAD", current_branch]:
                    new_line = f"{name}={commit_id}\n"
                    file_content[i] = new_line
                if line.startswith("HEAD="):
                    head_id = line.split("=")[1]
                    parent = head_id
        with open(reference_file, "w") as rf_name:
            rf_name.writelines(file_content)
        id_file_name = images_folder / commit_id
        id_file_name = str(id_file_name) + ".txt"
        id_file_info = (
            f"parent={parent}\n{print_now}\nmessage={cmd_line_list[2]}")
        with open(id_file_name, "w") as id_file:
            id_file.writelines(id_file_info)
            staging_area = closest_wit / "staging_area"
        copy_tree(staging_area, str(commit_id_image_folder))
        print(f"{staging_area} Copied")
        return id_file_name, parent, print_now


def check_ref_file(closest_wit):
    reference_file = closest_wit / "references.txt"
    if os.path.isfile(reference_file):
        return True


def create_commit_id():
    commit_id = ''.join(random.choice('1234567890abcdef') for i in range(40))
    closest_wit = find_closest_wit(current_folder)
    images_folder = closest_wit / "images"
    commit_id_image_folder = images_folder / commit_id
    return commit_id, images_folder, commit_id_image_folder


def add(path):
    print("add initiated...")
    path2 = current_folder / path
    if os.path.exists(path2):
        if os.path.isfile(path2) or os.path.isdir(path2):
            print("Copying file/directory")
            copy_file(path2)
            return "Done"
    else:
        print("not a file or directory")


def copy_file(path2):
    print("copy items...")
    closest_wit = find_closest_wit(path2)
    closest_wit_tree = str(closest_wit)
    closest_wit_tree = closest_wit_tree[:-4]
    if closest_wit is False:
        print("No wit folder. your files might not be backed-up")
        return

    staging_area = closest_wit / "staging_area"
    for dirpath, dirnames, filenames in os.walk(closest_wit_tree, topdown=True):
        structure = os.path.join(staging_area, dirpath[len(closest_wit_tree):])
        dirnames[:] = [dirname for dirname in dirnames if dirname != '.wit']
        new_folder = staging_area / structure
        if not os.path.isdir(new_folder):
            print(new_folder)
            os.mkdir(new_folder)
    if os.path.isfile(path2):
        filename = os.path.basename(path2)
        shutil.copy(filename, staging_area)
        print(f"{filename} Copied")


def find_closest_wit(path2):
    p = pathlib.Path(current_folder)
    i = 0
    while i < len(p.parents):
        for dirpath, dirnames, _filenames in os.walk(p.parents[i]):
            for dirname in dirnames:
                if dirname == ".wit":
                    closest_wit = os.path.join(dirpath, dirname)
                    return Path(closest_wit)
            i += 1
        print("No 'wit'")
        return None


def create_activated_file(newpath):
    print("Creating activated file")
    activated_file = newpath / "activated.txt"
    with open(activated_file, "w") as ac_file:
        ac_file.writelines("master")


def init():
    newpath = current_folder / ".wit"
    images = newpath / "images"
    staging_area = newpath / "staging_area"
    if not os.path.exists(newpath):
        for directory in [newpath, images, staging_area]:
            os.makedirs(directory)
    create_activated_file(newpath)


start()