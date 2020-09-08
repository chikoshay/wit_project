# upload 177
import datetime
from distutils.dir_util import copy_tree
import filecmp
import os
import pathlib
from pathlib import Path
import random
import shutil
import sys

import matplotlib.pyplot as plt


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


def merge(cmd_line_list):
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    else:
        branch_name = cmd_line_list[2]
        print(branch_name)


def branch(cmd_line_list):
    closest_wit = find_closest_wit(current_folder)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    else:
        branch_name = cmd_line_list[2]
        if check_ref_file(closest_wit):
            reference_file = closest_wit / "references.txt"
            if os.path.isfile(reference_file):
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
        master_id = find_master(closest_wit)
        parent = find_parent(master_id, closest_wit)
        _fig, ax = plt.subplots()
        ax.scatter([50, -50], [0, 0], s=10000)
        ax.text(30, -0.001, parent[:6], color='white', size=16)
        ax.text(-70, -0.001, master_id[:6], color='white', size=16)
        ax.set_xlim([-100, 100])
        ax.arrow(20, 0, -30, 0, head_width=0.01,
                 head_length=5, fc='blue', ec='blue')
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


def checkout(cmd_line_list):
    current_commit_id = cmd_line_list[2]
    closest_wit = find_closest_wit(current_folder)
    current_branch = check_activeted_file(closest_wit)
    if closest_wit is None:
        print("No wit folder. your files might not be backed-up")
    if current_commit_id == "master":
        current_commit_id = find_master(closest_wit)
    if find_closest_wit(current_folder):
        print("checkout test")
        requested_commit_id = current_commit_id
        print(requested_commit_id)
        commit_id_image_folder = closest_wit / "images" / current_commit_id
        if os.path.isdir(commit_id_image_folder):
            dcmp_original, dcmp_image = folder_diff(requested_commit_id)
            print('Changes to be committed      :', dcmp_image.left_only)
            print('Changes not staged for commit:', dcmp_original.diff_files)
            print('Untracked files:             :', dcmp_original.right_only)
            if len(dcmp_image.left_only) or len(dcmp_original.diff_files) > 0:
                print("As my mamma said: 'You need to commit first'")
        if current_commit_id == current_branch:
            print(current_commit_id)
            print("need to do stuff")
        if check_ref_file(closest_wit):
            reference_file = closest_wit / "references.txt"
            with open(reference_file, "r") as rf_name:
                lines_in_file = rf_name.readlines()
                for line in lines_in_file:
                    if line.startswith(cmd_line_list[2]):
                        print(line)
                        update_activeted_file(closest_wit, cmd_line_list[2])
        else:
            print(f"{requested_commit_id} is not a real backup. nice try.")


def folder_diff(current_commit_id):
    closest_wit = find_closest_wit(current_folder)
    if current_commit_id == "MASTER":
        print("Master")
    else:
        commit_id_image_folder = closest_wit / "images" / current_commit_id
        staging_area = closest_wit / "staging_area"
        print(staging_area)
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
                    write_ref_file(closest_wit, current_commit_id)


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
    active_id = None
    parent_wit = find_closest_wit(current_folder)
    if parent_wit is None:
        print("No wit folder. Please backup soon...")
    else:
        commit_id, closest_wit, images_folder, commit_id_image_folder = create_commit_id()
        if os.path.isdir(commit_id_image_folder):
            print("You've randomed twice... fill the lottory now!")
            commit_id, closest_wit, images_folder, commit_id_image_folder = create_commit_id()
        else:
            os.makedirs(commit_id_image_folder)
            now = datetime.datetime.now()
            print_now = now.strftime("%A %b %d %H:%M:%S %Y %z")
            reference_file = closest_wit / "references.txt"
            current_branch = check_activeted_file(closest_wit)
            if os.path.isfile(reference_file):
                print("Addind to old reference")
                with open(reference_file, "r") as rf_name:
                    lines_in_file = rf_name.readlines()
                    for line in lines_in_file:
                        if line.startswith("HEAD="):
                            old_commit_id = line[5:]
                            parent = old_commit_id
                        if line.startswith(current_branch):
                            active_id = line.split("=")[1]
            else:
                parent = "None"
            if active_id is not None:
                if current_branch == active_id:
                    with open(reference_file, "r") as rf_name:
                        file_content = rf_name.readlines()
                        print(file_content)
                        new_file_content = file_content[2:]
                    with open(reference_file, "w") as rf_name:
                        rf_name.writelines(
                            f"HEAD={commit_id}\nmaster={commit_id}\n")
                    with open(reference_file, "a") as rf_name:
                        for line in new_file_content:
                            rf_name.writeline(line)
            id_file_name = images_folder / commit_id
            id_file_name = str(id_file_name) + ".txt"
            id_file_info = (
                f"parent={parent}\n{print_now}\nmessage={cmd_line_list[2]}")
            with open(id_file_name, "w") as id_file:
                id_file.writelines(id_file_info)
                staging_area = closest_wit / "staging_area"
                copy_tree(staging_area, str(commit_id_image_folder))
                print(f"{staging_area} Copied")


def check_ref_file(closest_wit):
    reference_file = closest_wit / "references.txt"
    if os.path.isfile(reference_file):
        print("file excisets")
        return True


def create_commit_id():
    commit_id = ''.join(random.choice('1234567890abcdef') for i in range(40))
    closest_wit = find_closest_wit(current_folder)
    images_folder = closest_wit / "images"
    commit_id_image_folder = images_folder / commit_id
    return commit_id, closest_wit, images_folder, commit_id_image_folder


def add(path):
    print("add initiated")
    path2 = current_folder / path
    if os.path.exists(path2):
        if os.path.isfile(path2) or os.path.isdir(path2):
            print("Copying file/directory")
            copy_file(path2)
            return "Done"
    else:
        print("not file")


def copy_file(path2):
    print("copy file...")
    closest_wit = find_closest_wit(path2)
    if closest_wit is False:
        print("No wit folder. your files might not be backed-up")
    else:
        staging_area = closest_wit / "staging_area"
        if os.path.isfile(path2):
            filename = os.path.basename(path2)
            shutil.copy(filename, staging_area)
            print(f"{filename} Copied")
        if os.path.isdir(path2):
            shutil.copytree(path2, staging_area)
            print(f"{path2} Copied")


def find_closest_wit(path2):
    p = pathlib.Path(current_folder)
    i = 0
    while i < len(p.parents):
        for dirpath, dirnames, filenames in os.walk(p.parents[i]):
            # this line is just to make "filenames" useless as _
            filenames = filenames
            for dirname in dirnames:
                if dirname == ".wit":
                    closest_wit = os.path.join(dirpath, dirname)
                    return Path(closest_wit)
            i += 1
        print("No 'wit'")
        return False


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
