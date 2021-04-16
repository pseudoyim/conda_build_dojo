# Conda-Build Dojo

**/ˈdōˌjō/**<br>
*noun*<br>
a hall or place for immersive learning or meditation.

*Conda-Build Dojo* walks you through lessons that re-create scenarios encountered during package building.


[Requirements](#requirements)<br>
[Setup](#setup)<br>
[Getting updates](#getting-updates)<br>
[How to contribute a lesson](#how-to-contribute-a-lesson)<br>
[Development](#development)


## Requirements
- A system running some Unix variant (e.g. MacOS or Linux)
- Docker


## Setup 
**NOTE**: Only `linux-64` and `noarch` lessons are supported at this time.

1. Fork this repo to your personal Github account.
2. Clone your forked repo to your local machine (e.g. your Mac), preferably the same directory as `aggregate`.
3. From the `conda_build_dojo` root directory, run these steps to set up your remote sources:
    - Check the remote source of your repo (you should only see `origin`, pointing to the repo under your Github account).
        ```
        git remote -v
        ```
    - Add a new remote source, called `upstream`, pointed at the URL of the *original* repo.
        ```
        git remote add upstream git@github.com:anaconda-distribution/conda_build_dojo.git
        ```
    - Check the remote sources again. You should now see `origin` *and* `upstream`.
        ```
        git remote -v
        ```
4. Build the Docker image.
    ```
    docker build --network=host -t dojo_c3i_linux_64 ./docker_images/c3i-linux-64/
    ```
5. Run the Docker container, mounted to the local directory on your host that is the parent to `aggregate` and `conda_build_dojo`.
    ```
    docker run -it --mount 'src=</absolute/path/to/conda_build_dojo_and_aggregate_parent>,target=/home/,type=bind' dojo_c3i_linux_64

    # EXAMPLE (if `aggregate` and `conda_build_dojo` share the same parent directory called `projects`):
    docker run -it --mount 'src=/Users/pyim/shared/projects/,target=/home/,type=bind' dojo_c3i_linux_64
    ```
6. You should now be in the container. Run:
    ```
    start
    ```
    This will install `dojo` and its dependencies. If you get an error, double-check that you mounted from the correct directory in the previous step.
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
10. As you complete lessons in `dojo`, save your progress by committing and pushing to your personal `origin` repo. (Do this from your host machine - *not* from the Docker container).
    ```
    git push origin main
    ```
11. If you exit your container, you can re-run it using the command in Step 5. If your iamge gets destroyed, you can rebuild it using the command in Step 4.

### Getting updates
In the future, when you need to pull updates from the upstream repo (e.g. new lessons, bug fixes, or enhancements), run this form your host machine (**not** the Docker container):
```
git pull upstream main
```
Then, if you have a running container, run this to re-install `dojo` with the updates:
```
start
```

## How to contribute a lesson
1. From your host machine, checkout a dev branch.
2. From the Docker container, run:
    ```
    dojo create_lesson --name <LESSON_NAME>
    ```
3. Fill out all of the sections in the `lesson.yaml`.
4. (OPTIONAL) If your lesson requires `dojo_channels` (e.g. fake channels that recreate the channel conditions for your lesson), create and populate a `dojo_channels_pkgs.txt` file in your lesson directory.
    - In a separate terminal session, create a conda env (e.g. `test_env`) with your target package installed in it. Make sure to include all `build`, `host`, `run`, and `test` requirements. This will capture the *full* set of packages you need to build your target package in `dojo`.
    - After the env is created, run: `conda list -n test_env --explicit`
    - Copy and paste the list of URLs into the `dojo_channel_pkgs.txt` file.
        - Delete the URLs for any packages that should be removed for the lesson (i.e. the packages that the learner is expected to debug or build on their own).
5. Test your lesson (e.g. try out each step yourself).
6. Add your lesson to the `curriculum.yaml` under one of the topics.
7. Run `dojo clean` (to get rid of any progress and history that should not be committed upstream).
8. Commit and push your changes to the [upstream repo](https://github.com/anaconda-distribution/conda_build_dojo).
    ```
    git push upstream <YOUR DEV BRANCH>
    ```
9. Create a PR.


## Development
If you're planning to make a change to the [upstream repo](https://www.github.com/anaconda-distribution/conda_build_dojo), do the following:
1. From your host machine, checkout a dev branch.
2. Make your changes.
3. Test your changes in the Docker container.
4. Run `dojo clean` (to get rid of any progress and history that should not be committed upstream).
5. Commit and push your changes to the [upstream repo](https://www.github.com/anaconda-distribution/conda_build_dojo).
    ```
    git push upstream <YOUR DEV BRANCH>
    ```
6. Create a PR.


## TODO
- Lesons to add:
    - Create a patch (including on GitHub using .patch extension!)
    - Port a patch
    - Oniguruma (upstream breaking change)
    - How to inspect a failed build (e.g. build_env, h_env)
    - Checking the license type in a meta.yaml (Anju's example with pg8000-feedstock)
