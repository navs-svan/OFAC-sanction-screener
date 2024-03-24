# WSL Installation

* Check if WSL is installed in your computer
    * `wsl --list` 
* Look at list of available distributions to install
    * `wsl --list -o`
    * `-o` stands for online
* Install a distribution
    * `wsl --install -d <DISTRIBUTION>`
* Run a distribution
    * `wsl -d <DISTRIBUTION>`

# Linux Commands

* Switch to root user
    * `sudo su`
    * sudo means to run a command based on the root access that we have
    * sudo su goes to the root directory, commands ran here do not need `sudo`
* Update packages in distribution
    * `apt update && apt upgrade`
    * `apt update`: updates the list of available packages and their versions, but it does not install or upgrade any packages
    * `apt upgrage`: installs newer versions of the packages you have. After updating the lists, the package manager knows about available updates for the software you have installed.
* Install vsftpd (very secure file transfer protocol)
    * `apt install vsftpd`
* List files in root directory
    * `ls /etc/`
    * Take note of *vsftpd.conf* (config file of vsftpd)
* Make a backup of *vsftpd.conf*
    * `cp /etc/vsftpd.conf /etc/vsftpd.conf_original`
    * `cp <file_to_be_copied>  <destination_file>` 
* Open *vsftpd.conf*
    * `nano /etc/vsftpd.conf`
    * edit the following configurations
        ```
        local_enable=YES
        write_enable=YES
        chroot_local_user=YES
        chroot_list_enable=YES
        chroot_list_file=/etc/vsftpd.chroot_list # or just uncomment
        ssl_enable=YES
        require_ssl_reuse=NO # add to the bottom of the file
        force_local_logins_ssl=NO
        force_local_data_ssl=NO
        ```
    * _CTRL-S_ + _CTRZ-X_ to save and exit the text editor
* Restart service of vsftpd (EVERY CHANGES MADE)
    * `systemctl restart vsftpd`
* Check status of vsftpd
    * `systemctl status vsftpd`
* Create chroot_list 
    * `touch /etc/vsftpd.chroot_list`
    * chroot changes the apparent root directory for the current running process and its children. A program that is run in such a modified environment cannot name files outside the designated directory tree
* Create FTP user
    * `adduser ftpuser`
    * Password: password
* Create directory for exercise
    * `mkdir /home/ftpuser/ftp`
* Change ownership of folder to nobody
    * `chown nobody:nogroup /home/ftpuser/ftp`
* Change access of users in ftp folder
    * `chmod a-w /home/ftpuser/ftp`
    * a: all possible users
    * w: change or delete a file
    * a-w: remove all writing privileges from any group
* Add FTP user to `vsftpd.chroot_list`
    * `echo "ftpuser" | sudo tee -a /etc/vsftpd.chroot_list`
    * This user can only access the home directory of ftpuser `/home/ftpuser/`
