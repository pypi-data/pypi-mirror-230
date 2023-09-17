from pyPhases import PluginAdapter
from pyPhasesRecordloader import RecordLoader


class Plugin(PluginAdapter):
    def initPlugin(self):
        # self.project.loadConfig(self.project.loadConfig(pathlib.Path(__file__).parent.absolute().joinpath("config.yaml")))
        module = "pyPhasesRecordloaderSHHS"
        rlPath = f"{module}.recordLoaders"
        RecordLoader.registerRecordLoader("RecordLoaderSHHS", rlPath)
        RecordLoader.registerRecordLoader("SHHSAnnotationLoader", rlPath)
        shhsPath = self.getConfig("shhs-path")
        self.project.setConfig("loader.shhs.filePath", shhsPath)
        self.project.setConfig(
            "loader.shhs.dataset.downloader.basePath",
            shhsPath + "/polysomnography/edfs/shhs1",
        )
        self.project.setConfig(
            "loader.shhs.dataset.downloader.basePathExtensionwise",
            [
                shhsPath + "polysomnography/edfs/shhs1",
                shhsPath + "polysomnography/annotations-events-nsrr/shhs1",
            ],
        )

        self.project.setConfig(
            "loader.shhs2.dataset.downloader.basePath",
            shhsPath + "/polysomnography/edfs/shhs2",
        )
        self.project.setConfig(
            "loader.shhs2.dataset.downloader.basePathExtensionwise",
            [
                shhsPath + "polysomnography/edfs/shhs2",
                shhsPath + "polysomnography/annotations-events-nsrr/shhs2",
            ],
        )
