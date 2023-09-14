import pyroherd


class Update:
    def stop_propagation(self):
        raise pyroherd.StopPropagation

    def continue_propagation(self):
        raise pyroherd.ContinuePropagation
