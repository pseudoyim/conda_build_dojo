# Conda-Build Dojo

**/ˈdōˌjō/**<br>
*noun*<br>
a hall or place for immersive learning or meditation.

*Conda-Build Dojo* walks you through lessons that re-create scenarios encountered during package building.

## TODO

- Show all lessons (in curriculum.yaml)
- Show my history.

- Patch conda to make it download packages from defaults on Anaconda.org even if the .condarc points to a local file:/// repodata.json.
- Utility to remove packages from repodata.json (by filename, namespace, version numbers)
- When starting a lesson with modified_repodata, update their .condarc (back up the existing with "bak_20210202")
- Modify repodata (start, stop)

## Installation

From this repo's root directory:

1. Create the conda environment.
```
conda env create --file env.yaml
```

1. Activate the conda environment.
```
conda activate dojo_dev
```

1. Install this repo in dev mode.
```
pip install -e .
```

## Design
- Snapshots in time:
    - Packages in Repo: repodata.json
    - Recipes in AnacondaRecipes: commits
- The learner makes their own fork of this repo and clones it on target platforms.
- Run `dojo` and follow objectives and steps to complete lessons.

## Platforms

### Linux

1. Fork this repo to your personal account.
1. Run the `c3i_linux` Docker image to spin up a container.
1. Clone this repo onto the container.
1. Install dev mode (`pip install . -e`)
1. Run `dojo`.

### OSX

1. Use <Concourse training node?>

### Windows

1. Use <Concourse training node?>

## Create a lesson

Run:
```
dojo create_lesson --name <LESSON_NAME> [--repodata-snapshot --target-platform <TARGET_PLATFORM>]
```




To prune/edit repodata:
```
dojo prune_repodata

--subdir
--filenames, -f
--namespaces, -n
--versions, -v

```
