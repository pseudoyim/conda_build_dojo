# Conda-Build Dojo

**/ˈdōˌjō/**<br>
*noun*<br>
a hall or place for immersive learning or meditation.

*Conda-Build Dojo* walks you through lessons that re-create scenarios encountered during package building.

## Setup 
NOTE: Only `linux-64` is supported at this time.

1. Fork this repo to your personal Github account.
2. Clone your forked repo to your local machine (e.g. your Mac), preferably the same directory as `aggregate`.
3. From the `conda_build_dojo` root directory, run these steps to set up your remote sources:
    - Check the remote source of your repo (you should only see `origin`, pointing to the repo under your Github account).
    ```
    git remote -v
    ```
    - Add a new remote source, called `upstream`, pointed at the URL of the *original* repo.
    ```
    git remote add upstream https://github.com/anaconda-distribution/conda_build_dojo.git
    ```
    - Now check the remote sources. You should see `origin` *and* `upstream`.
    ```
    git remote -v
    ```
4. Build the Docker image.
```
docker build --network=host -t dojo_c3i_linux_64 ./docker_images/c3i-linux-64/
```
5. Run the container, mounted to a local directory on your host that can reach `aggregate` and `conda_build_dojo`.
```
docker run -it --mount 'src=</absolute/path/to/conda_build_dojo_and_aggregate_parent>,target=/home/,type=bind' dojo_c3i_linux_64 /bin/bash -c 'cd /home/conda_build_dojo; pip install -e .

# EXAMPLE (if `aggregate` and `conda_build_dojo` share the same parent directory called `shared`):
docker run -it --mount 'src=/Users/pyim/shared/,target=/home/,type=bind' dojo_c3i_linux_64 /bin/bash -c 'cd /home/conda_build_dojo; pip install -e .
```
6. Install `dojo`.
```
pip install -e .
```
7. Confirm `dojo` is installed.
```
dojo --help
```
8. View lessons.
```
dojo lessons
```
9. Start a lesson.
```
dojo start <LESSON NAME>
```
10. As you complete lessons in `dojo`, save your progress by committing and pushing to your `origin` repo.
```
git push origin main
```

### Getting updates
In the future, when you need to pull updates from the upstream repo (e.g. new lessons, bug fixes, or enhancements), run:
```
git remote pull upstream main

# Re-install with the latest updates.
pip install -e .
```

OBSOLETE:
1. Pull and run the [`c3i-linux-64`](https://github.com/conda/conda-concourse-ci/tree/master/docker/c3i-linux-64) Docker image to spin up a container, mounted to a path that can reach your clone of this `conda_build_dojo` repo and `aggregate`.
```
docker pull conda/c3i-linux-64:latest

docker run -it --mount 'src=<PATH THAT CAN ACCESS THE REPOS ON HOST MACHINE>,target=/home/,type=bind' conda/c3i-linux-64 /bin/bash

  EXAMPLE:
  docker run -it --mount 'src=/Users/pyim/shared/projects/,target=/home/,type=bind' conda/c3i-linux-64 /bin/bash
```
2. In the container, do the following:
    - Update `conda-build`: `conda update -y conda-build`
    - Go to the repo: `cd <PATH TO>/conda_build_dojo`
    - Pip install the repo and its deps in dev mode: `pip install -e .`
    - Pip install `python-tabulate` from its github source: `pip install git+https://github.com/astanin/python-tabulate.git`
    - Run: `dojo --help`. If you see the help message, you're ready to roll.



## How to contribute a lesson

1. Checkout a dev branch.
2. Run:
```
dojo create_lesson --name <LESSON_NAME>
```
3. Fill out the `lesson.yaml`.
4. (OPTIONAL) If your lesson requires `dojo_channels` (e.g. fake channels that recreate the channel conditions for your lesson), create and populate a `dojo_channels_pkgs.txt` file in your lesson directory.
    - Create a conda env (e.g. `test_env`) with your target package installed in it. Make sure to include all `build`, `host`, `run`, and `test` requirements. This will capture the *full* set of packages you need to build your target package in `dojo`.
    - Afte the env is created, run: `conda list -n test_env --explicit`
    - Copy and paste the list of URLs into the `dojo_channel_pkgs.txt` file.
        - Delete the URLs for any packages that should be removed for the lesson (i.e. the packages that the learner is expected to build on their own).
5. Test your lesson (e.g. try out each step yourself).
6. Add your lesson to the `curriculum.yaml` under one of the topics.
7. Run `dojo clean` (to get rid of any progress and history that should not be committed upstream).
8. Commit and push your changes to the [upstream repo](`github.com/anaconda-distribution/conda_build_dojo`).
```
git push upstream <YOUR DEV BRANCH>
```
9. Create a PR.


## Development

1. Spin up the `c3i_linux-64` docker image, mounted to a path that can reach your clone of the repo and `aggregate`.
2. From this repo's root directory, create the conda environment.
```
conda env create --file env.yaml
```
3. Activate the conda environment.
```
conda activate dojo_dev
```
4. Install this repo in dev mode.
```
pip install -e .
```
5. If you're planning to make a change to the [upstream repo](`github.com/anaconda-distribution/conda_build_dojo`), do the following:
    1. Checkout a dev branch.
    1. Make your changes.
    1. Test your changes.
    1. Run `dojo clean` (to get rid of any progress and history that should not be committed upstream).
    1. Commit and push your changes to the [upstream repo](`github.com/anaconda-distribution/conda_build_dojo`).
    ```
    git push upstream <YOUR DEV BRANCH>
    ```
    1. Create a PR.


## TODO
- Create a Dockerfile to save in this repo (see example from QLib).
- Move this repo to the anaconda-distribution org.
- Lesons to add:
    - Create a patch (including on GitHub using .patch extension!)
    - Port a patch
    - Oniguruma (upstream breaking change)
    - How to inspect a failed build (e.g. build_env, h_env)
    - Checking the license type in a meta.yaml (Anju's example with pg8000-feedstock)
