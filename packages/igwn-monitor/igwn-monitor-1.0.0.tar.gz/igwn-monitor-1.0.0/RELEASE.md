# Releasing `igwn-monitoring-plugins`

The instructions below detail how to finalise a new release
for version `{X.Y.Z}`.

In all commands below that placeholder should be replaced
with an actual release version.

## 1. Update the packaging files

-   Create a new branch on which to update the OS packaging files:

    ```shell
    git checkout -b finalise-{X.Y.Z}
    ```

-   Bump the version number in the following files:

    - `CMakeLists.txt`
    - each of the `scripts/`

-   Add new changelog entries in OS packaging files:

    - `debian/changelog`
    - `rpm/nagios-monitoring-plugins.spec.in`

    and then commit the changes to the branch.

-   Push this branch to your fork:

    ```shell
    git push -u origin finalise-{X.Y.Z}
    ```

-   Open a merge request on GitLab to finalise the packaging update.

## 2. Tag the release

-   Draft release notes by looking through the merge requests associated
    with the relevant
    [milestone on GitLab](https://git.ligo.org/duncanmmacleod/igwn-monitoring-plugins/-/milestones).

-   Create an annotated, signed tag in `git` using the release notes
    as the tag message:

    ```shell
    git tag --sign {X.Y.Z}
    ```

-   Push the tag to the project on GitLab:

    ```shell
    git push -u upstream {X.Y.Z}
    ```

## 3. Create a Release on GitLab

-   Create a [Release on GitLab](
    https://git.ligo.org/duncanmmacleod/igwn-monitoring-plugins/-/releases/new
    ), copying the same release notes from the tag message.

    Make sure and correctly associated the correct Tag and Milestone to
    the Release.

## 4. Publish the new distribution on software.igwn.org:

-   Upload the igwn-monitoring-plugins-X.Y.Z.tar.xz source distribution to
    the IGWN Software Archive according to the latest instructions on

    <https://computing.docs.ligo.org/guide/software/distribution/#upload>
