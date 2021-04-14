# shargain - Ansible

This playbook configures server and deploys shargain

## Requirements

Install role requirements with the following command:

    ansible-galaxy install -r roles/requirements.yml --roles-path=roles

Put vault password into `~/.ansible/shargain.vault` file.

## Usage

Before runnning any ansible playbook you should always run with
`--check` flag to see if it makes any changes.

To configure server as well as deploy app, run:

         ansible-playbook -i inventory.txt shargain.yml --diff --check

By default `master` tag is used for docker image. To deploy
only docker container with any tag, invoke:

       ansible-playbook -i inventory.txt shargain.yml -t docker -e "_docker_tag=<tag_name>" --diff --check


Above commands are with `--check` flag. To apply changes, remove it.

## License
[BSD](LICENSE)

## Authors
[nekeal](https://github.com/nekeal)
