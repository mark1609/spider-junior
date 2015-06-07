import input
import task

if __name__ == "__main__":
    # load parameter from command line
    argRun = input.arg()
    input.initParam(argRun)

    # start main task
    task = task.task(argRun)
    task.run()
