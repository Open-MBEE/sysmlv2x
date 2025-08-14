package Demo {
    state def A_behavior {
        attribute def GoOnline{}
        attribute def GoOffline{}
        
        entry; then OFF; // defines OFF as initial state 
        state OFF {}
        state ONLINE {
            do action ActivityOnline {}
        }

        transition off_to_online first OFF
            accept GoOnline // GoOnline is the event 
            then ONLINE;
        transition online_to_off first ONLINE
            accept GoOffline // GoOffline is the event 
            then OFF;
    }
}
