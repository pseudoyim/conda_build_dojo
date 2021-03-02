# Conda-Build Dojo

**/ˈdōˌjō/**
*noun*
a room or hall in which judo and other martial arts are practiced.

## TODO
- Every new action is tracked in history.csv
- Utility to add repodata snapshot to a lesson
- Utility to remove packages from repodata.json (by filename, namespace, version numbers)

## Development

To create the dev environment, run:
```
conda env create --file env.yaml
```

## Directory structure
```
conda_build_dojo/
  |---- dojo/
  |---- lessons/
      |---- 0001_version_bump/
              |---- lesson.yaml (contains lesson metadata, subdirs to use, tags, description, objectives, docker image or VM to use, git commit to checkout, questions and prompts, hints)
              |---- progress.csv (tracks your actions INSIDE the lesson, along with your notes)
              |---- repodata/
                      |---- linux-64/
                              |---- repodata.json
                      |---- noarch/
                              |---- repodata.json
      |---- 0002_fix_hash/
      |---- 0003_failing_test/
      |---- 0004_missing_dependencies/
  |---- training_feedstocks/
  |---- curriculum.yaml
  |---- env.yaml
  |---- history.csv (tracks your actions AMONG lessons)
  |---- README.md
```

## Design

- The builder makes their own fork.

- Objective for the builder.

- Snapshots in time:
    - Packages in Repo: repodata.json
    - Recipes in AnacondaRecipes: commits

- `curriculum.yaml` at root dir contains:
    - Topic
        - Lesson (lessons will be numbered dynamically based on order in yaml)
        - Lesson
        - Lesson
    - Topic
        - Lesson
        - Lesson
        - Lesson
    - Contains any metadata that displays when user runs `dojo lessons`
        - Version number.
        - 


## Platforms

### Linux

Use the c3i_linux Docker image.

### OSX

Use <Concourse training node?>

### Windows

Use <Concourse training node?>


## Usage

Fork this repo.

### View my history
Shows lessons you've started and completed. (References the history.csv)
```
$ dojo history
```

### View lessons
References curriculum.yaml, displaying all available lessons.
```
$ dojo lessons
```

### Review a lesson
References the lesson's lesson.yaml and progress.yaml.
```
$ dojo review <LESSON DIR NAME - lazy ok>
```

### Navigation options

#### Start lesson
```
$ dojo start <LESSON DIR NAME - lazy ok>

Starting Conda-Build Dojo...

Setting up feedstock snapshot...
Cloning <FEEDSTOCK NAME> at <COMMIT>
...success!

Setting up repo snapshot...
Updating your .condarc to point to repodata snapshot from <TIMESTAMP> for the following subdirs:
- noarch
- <SUBDIR>
...success!

##################################

Welcome to the Dojo!

Lesson: "How to do a version bump"
Objective: Build an updated version of tqdm.

Package: tqdm-1.2.3
Target platform: noarch

STEP 1: Open the meta.yaml and find the current verion and sha256 hash.

Options: 
dojo (p)revious step; (c)urrent step; (n)ext step; (a)dd note; e(x)it lesson.

$
```

#### Next step
Not passing --verbose will just show the step and options.
```
$ dojo n --verbose

Lesson: "How to do a version bump"
Objective: Build an updated version of tqdm.

Package: tqdm-1.2.3
Target platform: noarch

STEP 2: Go to the tqdm project's PyPI page and get the new hash for version 1.2.4.

Options: 
dojo (p)revious step; (c)urrent step; (n)ext step; (a)dd note; e(x)it lesson.

$ 
```







