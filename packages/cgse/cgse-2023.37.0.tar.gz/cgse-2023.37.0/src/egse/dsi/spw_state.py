class SpaceWireLinkState:
    def __init__(self):
        self.linkDisabled = True
        self.linkStart    = False
        self.autoStart    = False
        self.gotNULL      = False

    def isEnabled(self):
        return not self.linkDisabled and (self.linkStart or self.autoStart and self.gotNULL)

    def setAutoStart(self):
        self.autoStart = True

    def unsetAutoStart(self):
        self.autoStart = False

    def setGotNull(self):
        self.gotNULL = True

    def unsetGotNULL(self):
        self.gotNULL = False

    def setLinkDisabled(self):
        self.linkDisabled = True

    def unsetLinkDisabled(self):
        self.linkDisabled = False

    