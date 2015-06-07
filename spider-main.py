import input
import task

if __name__ == "__main__":
    argRun = input.arg()

    # load parameter from command line
    input.initParam(argRun)

    # start main task
    task = task.task(argRun)
    task.run()
