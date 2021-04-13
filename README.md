# Conda-Build Dojo

**/ˈdōˌjō/**<br>
*noun*<br>
a hall or place for immersive learning or meditation.

*Conda-Build Dojo* walks you through lessons that re-create scenarios encountered during package building.

## Installation

### Linux

1. Fork this repo to your personal Github account.
1. Clone your fork of this repo locally (e.g. on your Mac).
1. Run the `c3i_linux-64` Docker image to spin up a container, mounted to a path that can reach your clone of this `conda_build_dojo` repo and `aggregate`.
1. In the container, `cd` to this repo, and install it in dev mode (`pip install . -e`)
1. Run `dojo --help`. If successful, you're ready to roll.

### OSX

(TBD)

### Windows

(TBD)

## Create a lesson

1. Run:
```
dojo create_lesson --name <LESSON_NAME>
```
1. Fill out the `lesson.yaml`.
1. (OPTIONAL) If your lesson requires `dojo_channels` (e.g. fake channels that recreate the channel conditions for your lesson), create and populate a `dojo_channels_pkgs.txt` file in the lesson directory.
    - Create an env with your target package installed in it. Make sure to include all build, host run, and test requirements. This will capture the FULL list of packages you need to build your target package in dojo.
    - Run: `conda list -n test_env --explicit`
    - Copy and paste the list of URLs into `dojo_channel_pkgs.txt`
        - Delete any URLs for the packages that should be removed for the lesson (i.e. the packages that the learner is expected to build).

## Design
- The learner makes their own fork of this repo and clones it.
- Snapshots in time:
    - Packages in Repo: Download needed packages into local directory and run "conda index" to pretend they're channels.
    - Recipes in AnacondaRecipes: commits
- Run `dojo` commands and follow objectives and steps to complete lessons.

## Development

1. Clone this repo to your local machine.
2. Spin up the `c3i_linux-64` docker image, mounted to a path that can  reach your clone of the repo and `aggregate`.
3. From this repo's root directory, create the conda environment.
```
conda env create --file env.yaml
```
4. Activate the conda environment.
```
conda activate dojo_dev
```
5. Install this repo in dev mode.
```
pip install -e .
```
6. If you're planning to make a change to the [upstream repo](`github.com/anaconda-distribution/conda_build_dojo`) (e.g. to contribute a new lesson), do the following:
	1. Checkout a dev branch.
	1. Make your changes.
	1. Test your changes.
	1. Run `dojo clean` (to get rid of any progress and history that shouldn't be committed upstream).
	1. Commit and push your changes to the upstream repo and create a PR.

## TODO
- dojo lessons 
	- Show lessons (in curriculum.yaml)
	- show "done", "started", "not started"
- Add color to the prompt (use colorama, add to env.yaml).
- Lesons to add:
    - Create a patch (including on GitHub!)
    - Port a patch
    - Oniguruma (upstream breaking change)
