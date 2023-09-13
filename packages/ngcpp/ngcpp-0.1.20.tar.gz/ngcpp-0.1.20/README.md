# Install

```shell
pip install ngcpp
sudo apt install fzf # iteractive fuzzy finder

# if apt installed fzf does not work or give strange behavior
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install
```

# Feature

## cluster `ngc_cluster --help`

* `ngc_cluster usage --help`: List user usage
* `ngc_cluster hang --help`: List your all hanging jobs
* `ngc_cluster list --help`: List your jobs in one cluster
* `ngc_cluster alias --help`: List all available cluster aliases

## job `ngc_job --help`

* `ngc_job kill --help`: kill your jobs interactively
* `ngc_job result --help`: download results for your jobs interactively
* `ngc_job bash --help`: exec bash for one selected job~(support autoresuming)


## resume `ngc_resume --help`


### Automated Job Resubmission

Utilize a "polling" mechanism to automatically resubmit your job under the following circumstances:
* The job is terminated by the system.
* The job encounters a failure.
* The job hangs.
By implementing this approach, you ensure that critical jobs are consistently reattempted,

### How to Use

To track a specific job, define it in the `ngc_resume.yaml` file as follows:

```yaml
"10": # Cluster alias, e.g., prd10
    ml-model.test_unet: # Job name; ensure that the job name matches the `--name` argument in the command line
        ngc batch run --name "ml-model.test_unet" --priority HIGH --order 50 --preempt RUNONCE --min-timeslice 0s --total-runtime 1209600s --ace nv-us-west-2 --instance dgxa100.40g.8.norm --commandline "sleep 10h" --result /result --array-type "PYTORCH" --replicas "18" --image "another_docker_image" --org your_org --team your_team
    ml-model.test_another_unet:
        # Define another job here

"77": # Cluster alias, e.g., prd77
    job_name: cmd
```

### Key Considerations:

* Ensure job names in one cluster is unique
* Ensure that the job name **matches** the --name argument in the command line.
* The `cmd` section can be copied from `https://bc.ngc.nvidia.com/jobs/{job_id}?tab=overview`.
* We determine hanging jobs by checking their TensorCore usage.

### TODO

- [ ] Implement a feature to automatically copy the command.
