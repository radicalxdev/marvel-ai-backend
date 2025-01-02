import os
import watchdog.events
import watchdog.observers
import time

class package_handler(watchdog.events.FileSystemEventHandler):
    '''
    - on_created : executed when a file or directory is created
    - event.src_path : returns the path in which the directory has been created
    - event.is_directory : checks if a new directory has been created, will ignore if a new file has been created
    '''
    def on_created(self, event):
        if event.is_directory:
            f = open(os.path.join(event.src_path, "__init__.py"), "w")  # initializes __init__.py file
            f.close()   # closes the open file
            print("new __init__.py created successfully!")


if __name__ == "__main__":
    '''
    - watchdog.observers.Observer() : Observer thread that schedules watching directories and dispathces calls to event handlers
    
    - watchdog.observers.Observer().schedule() : method used to register an event handler to monitor a specific path, the recurisve=True param ensures that subdirectories are monitored as well
    
    '''
    event_handler = package_handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=os.getcwd(), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:   # control + c keystroke is pressed
        observer.stop()
    observer.join()