
# Github debugging

## Questions to address
- Large files error
- If remote repo is ahead of local repo
- If local repo is ahead of remote repo

## Useful commands
```bash
git status # check the status of the repo
git log # check the commit history
git diff # check the difference between the current state and the last commit(HEAD)
git diff HEAD~2 yourfilename # check the difference between the current state and the 2nd last commit
```

## Delete a corrupted branch
It seems that accepting the pull request may have caused some corruption in your repository, resulting in the creation of a branch with an invalid name (`main 2`). Here’s how you can resolve the issue:

### Steps to Resolve the Invalid Branch Issue

1. **Delete the Invalid Branch Reference:**
   Manually delete the invalid branch reference.

   ```bash
   rm -f .git/refs/heads/main\ 2
   ```

2. **Clean Up Logs and References:**
   Clean up any logs or references that might be pointing to the invalid branch.

   ```bash
   rm -f .git/logs/refs/heads/main\ 2
   rm -f .git/logs/refs/remotes/origin/main\ 2
   ```

3. **Check Remaining Branches:**
   Verify the branches in your repository again.

   ```bash
   git branch
   ```

4. **Fetch and Reset the Main Branch:**
   Fetch the latest changes from the remote repository and reset your local main branch.

   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

5. **Rebase Local Changes:**
   If you have local changes that need to be incorporated, rebase them onto the updated main branch.

   ```bash
   git pull --rebase origin main
   ```


## Rewind to a previous commit
```bash
git checkout HEAD~2 yourfilename # revert the file to the 2nd last commit
```

Eg. If you put some files in to .gitignore, then you do `git pull --rebase origin main`. Those files will be likely to removed when git automatically dealing with conflict!!! Then you might need to:
```bash
git log -- <yourfilename> # to see during which commit did you delete the file
git checkout <commit hash> -- <yourfilename> # an example of commit hash can be cfb90ea932623b906a52724207a931c09c6e3312
```
Don't worry then you will see the file back in your local repo.

But be careful when you do not specify the filename!!!
```bash
git checkout f22b25e # revert the whole repo to the commit with the hash f22b25e
```

You will see the following message:
Note: checking out 'f22b25e'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -b with the checkout command again. Example:

```bash
git checkout -b <new-branch-name>
```

## Merge two branches
Say, we have two branches `main` and `local-pc`. Now we want to ensure that the `main` branch ends up exactly like the `local-pc` branch (effectively overwriting `main` with the state of `local-pc`), you can achieve this by using a combination of Git commands that ensure `main` is updated to exactly match `local-pc`. Here’s how you can do this step by step:

### Step 1: Checkout the Main Branch
First, make sure you are on the `main` branch:
```bash
git checkout main
```

### Step 2: Merge with the Option to Overwrite
To overwrite the changes in `main` with those from `local-pc`, you can use the `git merge` command with the `--strategy-option theirs` when doing a merge. This strategy will resolve all conflicts by preferring changes from the `local-pc` branch:

```bash
git merge local-pc -X theirs
```
However, note that the `-X theirs` option only affects how conflicts are resolved, not non-conflicting changes. If you absolutely need `main` to be a mirror image of `local-pc`, regardless of the state of `main`, a more forceful approach is to reset `main` to the state of `local-pc`:

### Step 3: Force Main to Match Local-PC (Alternative Method)
If you want to ensure that `main` exactly matches `local-pc` and are okay with rewriting the history of `main` (which is safe as long as you coordinate with your team if you're working collaboratively), you can use the following commands:

```bash
git checkout main
git reset --hard local-pc
```

This will reset the `main` branch to exactly match the state of `local-pc`, discarding any commits in `main` that are not in `local-pc`.

### Step 4: Push the Changes
After resetting or merging, if you want these changes to reflect in the remote repository, you'll need to push them. If you used `reset`, you'll need to use `--force` with your push because you have rewritten the history:

```bash
git push origin main --force
```

**Warning:** Using `--force` can disrupt other collaborators working on the same branch. It is recommended to communicate these changes with your team and ensure that no one else has unmerged changes on the `main` branch before you force-push.

### Important Considerations
- **Communication**: Before resetting a shared branch like `main` and force pushing, it's crucial to coordinate with anyone else who might be affected. Resetting a branch and force pushing can cause significant disruption to collaborative workflows.
- **Backup**: It's a good practice to ensure that there are backups of the data before performing operations that rewrite history, particularly on shared branches.

By following these steps, you can effectively overwrite the `main` branch with the state of `local-pc`, ensuring that `main` exactly reflects the state of `local-pc`.

## Keep asking for ssh passphrase
SSH Agent May Not Caching the Key:
Your SSH agent might not be caching your key, requiring you to enter the passphrase repeatedly. You can add your key to the SSH agent to avoid having to enter the passphrase every time you use the key. Here’s how you can do it:
```bash
eval "$(ssh-agent -s)"  # Start the ssh-agent in the background
ssh-add ~/.ssh/id_ed25519  # Add your SSH private key to the ssh-agent
```
After running these commands, your SSH key should be added to the SSH agent, and you should no longer be prompted for the passphrase when using the key.

## .gitignore not working
### rm cache
```bash
git rm -r --cached [files/folders]
```

### Additional cleaning
If the large files were previously committed to history and you need to reduce your repository size or ensure they are removed from all history (for example, if they contain sensitive information), you might need to rewrite history using git filter-branch, or use a tool like BFG Repo-Cleaner. This is especially important if your repository is close to or exceeding size limits on platforms like GitHub.

Here's a simple way to use git filter-branch to remove a folder from all commits:

```bash
git filter-branch --force --index-filter \
git rm --cached -r --ignore-unmatch 3_result/figures \
--prune-empty --tag-name-filter cat -- --all
```
After using git filter-branch, force push to your repository:

```bash
git push origin --force --all
```

Note on Using git filter-branch

Rewriting history with git filter-branch can affect all collaborators. They will need to rebase their work on top of the updated history. Communicate with your team before performing such actions.

By following these steps, you should be able to remove the large files from your repository, clean up your commit history if necessary, and prevent such files from being tracked in the future.

## Can't push to remote repository
### local repo is out-of-date
**We need to `pull` first**

1. Merging
This is the default behavior for git pull without specifying any configuration. It fetches the remote branch and then merges it into your local branch. Merging creates a merge commit in your history which shows where two divergent branches were brought together.

To pull with a merge:

```bash
git pull --no-rebase origin main
```

2. Rebasing
Rebasing rewrites your local changes to be on top of what is on the remote. This often makes the history cleaner as it appears as if all the changes were made in a linear sequence.

To pull with a rebase:

```bash
git pull --rebase origin main
```

3. Fast-Forward Only
If you prefer to avoid creating additional merge commits and want to ensure that your local changes create a linear history with the remote branch (assuming your changes could be applied directly on top of the base branch without divergence), you can opt for a fast-forward merge. This option will fail if there's no clear path to fast-forward, meaning it can't apply your local changes directly on top of the remote changes without needing a merge.

To pull with fast-forward only:

```bash
git pull --ff-only origin main
```

Setting a Default Pull Behavior

If you find yourself preferring one method over the others, you can set a default configuration for your repository or globally for all your Git repositories. Here's how to set each as a default:

Set merge as the default:

```bash
git config pull.rebase false
# Or globally
git config --global pull.rebase false
```

Set rebase as the default:

```bash
git config pull.rebase true
# Or globally
git config --global pull.rebase true
```

Set fast-forward only as the default:

```bash
git config pull.ff only
# Or globally
git config --global pull.ff only
```

By setting one of these configurations, future git pull commands will default to the behavior you've specified, eliminating the need to specify how to handle divergent branches each time. After pulling and resolving any conflicts (if necessary), you should be able to push your changes to the remote repository without any further issues.

## SSH key Setup
When generating an SSH key using `ssh-keygen`, you can specify the filename and location to save the key. Here’s how to do it:

### Step-by-Step Guide

1. **Open Terminal**:
   Open a terminal on your macOS.

2. **Run `ssh-keygen` Command**:
   Use the following command to start the key generation process:

   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

   Replace `your_email@example.com` with your actual email address.

3. **Specify the Filename**:
   When prompted for the file in which to save the key, you can specify a custom filename and location. For example, to save the key as `my_custom_key` in the `.ssh` directory, enter:

   ```plaintext
   Enter file in which to save the key (/Users/your_username/.ssh/id_rsa): /Users/your_username/.ssh/my_custom_key
   ```

   Replace `your_username` with your actual username.

4. **Complete the Key Generation**:
   You’ll be prompted to enter a passphrase. You can either enter a passphrase for additional security or leave it empty and press `Enter` for no passphrase.

   ```plaintext
   Enter passphrase (empty for no passphrase):
   Enter same passphrase again:
   ```

### Example:

Here’s a complete example of the process:

```plaintext
$ ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
Generating public/private rsa key pair.
Enter file in which to save the key (/Users/your_username/.ssh/id_rsa): /Users/your_username/.ssh/my_custom_key
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /Users/your_username/.ssh/my_custom_key.
Your public key has been saved in /Users/your_username/.ssh/my_custom_key.pub.
The key fingerprint is:
SHA256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_email@example.com
The key's randomart image is:
+---[RSA 4096]----+
| .o..   .        |
|  .+o . . .      |
| ..=o . o o      |
|..o= o   .       |
|ooE . . S        |
| o .. o = .      |
|  ..  o B        |
|   .o + o        |
|   .+o.o.        |
+----[SHA256]-----+
```

### Step 4: Update SSH Config File

After generating the key, update your `~/.ssh/config` file to use this new key:

1. **Open the SSH config file**:

    ```bash
    nano ~/.ssh/config
    ```

2. **Add an entry for your remote server**:

    ```plaintext
    Host myserver
        HostName remote_server
        User user
        IdentityFile ~/.ssh/my_custom_key
    ```

    Replace `myserver` with a name you want to use for the connection, `remote_server` with the server’s address, `user` with your username, and `my_custom_key` with the filename you specified.

3. **Save and exit the file** (`Ctrl + O`, `Enter`, `Ctrl + X`).

### Step 5: Copy the SSH Key to Your Remote Server

Copy your public key to the remote server:

```bash
ssh-copy-id -i ~/.ssh/my_custom_key.pub user@remote_server
```

Now, you should be able to connect to your remote server without entering a password:

```bash
ssh myserver
```

Using this method, you can customize the filename and location of your SSH key pair, making it easier to manage multiple keys for different servers.