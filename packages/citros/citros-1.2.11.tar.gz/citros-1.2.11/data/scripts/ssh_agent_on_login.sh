if ! pgrep -x "ssh-agent" >/dev/null; then
   # Launch a new instance of the agent
   ssh-agent -s &> $HOME/.ssh/ssh-agent

   # set up the SSH agent's environment
   eval `cat $HOME/.ssh/ssh-agent`
fi