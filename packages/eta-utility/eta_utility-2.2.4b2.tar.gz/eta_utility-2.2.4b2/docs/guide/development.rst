.. _development:

Contributing to development
===========================

Before contributing to development of *eta_utility*, please read this development
guide carefully. If you are looking for instructions on how to install *eta_utility* for usage
only, please take a look at the :ref:`install` guide.

If you need help installing python or git, please consult the :ref:`python_install` guide.

The most important things
-----------------------------

If you would like to contribute, please create an issue in the repository to discuss your suggestions.
Once the general idea has been agreed upon, you can create a merge request from the issue and
implement your changes there.

If you want to perform development work, specify the "develop" extension during installation.
This will install all packages required for development work and for the automated integration
checks.

We use pre-commit to check code before committing. Therefore, after installing *eta_utility* with
the develop extension and creating your virtual environment, please execute:

.. code-block:: console

    $> pre-commit install

If you are planning to develop on this package, based on the requirements of another
package, you might want to import directly from a local git repository. To do this,
uninstall eta_utility from the other projects virtual environment and add the path to the local
*eta_utility* repository to the other projects main file:

.. code-block::

    sys.path.append("<path to local eta_utility repository>")


Installation of eta_utility
-------------------------------------

Open a terminal for the next steps (such as PowerShell)

 .. note::
    Depending on where the relevant folders for the installation are located on your OS,
    the terminal may need to be executed as administrator / root.

First, clone the repository to a directory of your choosing. You can use a git GUI for this or
execute the following command. See also :ref:`install_git`.

.. code-block:: console

    $> git clone <Repository URL>

You might be asked for your git login credentials.

.. figure:: figures/10_GitLogin.png
    :width: 300
    :alt: git login

    Git login window.

.. warning::
    Due to limitations with the versions of *stable_baselines3* and *gym* this version of *eta_utility*
    can only be installed after executing the following command to install specific versions of
    *setuptools* and *pip*:

    .. code-block:: console

        $> python -m pip install setuptools==65.5 pip==21

After this, go to the root directory of the Git project and install the project with the
development extension. This includes all requirements plus everything required for development
and continuous integration checks:

.. code-block:: console

   $> pip install -e .[develop]

The installation process (except for the installation of pre-commit) is shown in the following
figure.

.. figure:: figures/13_InstallWithVE.PNG
    :width: 700
    :alt: installation within a virtual environment

    Installation of *eta_utility* within a virtual environment

After the installation completes, please install pre-commit before performing the first commits
to the repository. This ensures that your commits will be checked and formatted automatically.

.. code-block:: console

   $> pre-commit install

.. figure:: figures/11_PreCommit.png
    :width: 600
    :alt: pre-commit installed successfully

    Confirmation of correct pre-commit installation.

Testing your code
-------------------------------
Please always execute the tests before committing changes. You can do this by navigating to the main
folder of the *eta_utility* repository and executing pytest in a terminal. Make sure the virtual
environment is activated before this (see :ref:`create_virtual_environment`).

.. code-block:: console

    $> pytest

Editing this documentation
-----------------------------

Sphinx is used as a documentation-generator. The relevant files are located in the *docs*
folder of the repository. If you correctly installed *eta_utility* with the develop
extension, sphinx should already be installed.

You can edit the *.rst-files* in the *docs* folder. A simple text editor is sufficient for this.
A helpful start for learning the syntax can be found `here <https://sublime-and-sphinx-guide.readthedocs.io/en/latest/index.html>`_.

For test purposes, the following command can be executed in the directory of the documentation (on Windows you might need
to add './' before the command):

.. code-block:: console

    $> make html

This creates a folder named *_build* (inside the *docs* folder) which allows the HTML pages to
be previewed locally. This folder will not be committed to git. Re-execute this command each
time you edit the documentation to see the changes (you have to refresh the HTML page, too).

.. figure:: figures/dev_01_HTMLbuild.PNG
    :width: 700
    :alt: successful documentation build

    Confirmation for successful documentation build.

If you have problems using sphinx see :ref:`sphinx_not_found`.

GitLab - CI/CD
--------------------------------------

Your contribution via pull request can only be merged if the steps from the CI/CD are approved.
The stages are:

- *check*: verify the check-style
- *test*: check all tests
- *deploy*: verify correct documentation deploy

All the CI/CD instructions are listed in the *.gitlab-ci.yml* file.

GitLab - Docker containers
-----------------------------

The directory *.gitlab* contains the dockerfiles which defines the images that the jobs
of the CI/CD run on. Currently there are two main dockerfiles, one to describe python-julia
environment and another just for python.

All the dockerfiles contains an correspondent image stored in **Packages & Registries > Container Registry**.
In which the image will be used in a container to execute the jobs.

To update the containers first you need to login in GitLab throught docker.

.. code-block:: console

    $> docker login git-reg.ptw.maschinenbau.tu-darmstadt.de


Then you build the image from the dockerfile.

.. code-block:: console

    $> docker build -t git-reg.ptw.maschinenbau.tu-darmstadt.de/eta-fabrik/public/eta-utility/<image-name>:<tag> <directory-of-dockerfile>

Using tags for the images is a good practice to differentiate image versions, in case it's not used it's automatic labeled as *latest*.
Currently there are three images for python environments called *python_env*, with python versions differentiated by tags (3.8, 3.9 and 3.10).

The last step is to upload the images to the docker.

.. code-block:: console

    $> docker push git-reg.ptw.maschinenbau.tu-darmstadt.de/eta-fabrik/public/eta-utility/<image-name>:<tag>
