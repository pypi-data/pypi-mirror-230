from datoso.repositories.dat import XMLDatFile

systems = {
    'FinalBurn Neo - Arcade Games': 'arcade',
    'FinalBurn Neo - ColecoVision Games': 'coleco',
    'FinalBurn Neo - Fairchild Channel F Games': 'channelf',
    'FinalBurn Neo - FDS Games': 'fds',
    'FinalBurn Neo - Game Gear Games': 'gamegear',
    'FinalBurn Neo - Master System Games': 'sms',
    'FinalBurn Neo - Megadrive Games': 'megadrive',
    'FinalBurn Neo - MSX 1 Games': 'msx',
    'FinalBurn Neo - Neogeo Games': 'neogeo',
    'FinalBurn Neo - Neo Geo Pocket Games': 'ngp',
    'FinalBurn Neo - NES Games': 'nes',
    'FinalBurn Neo - PC-Engine Games': 'pce',
    'FinalBurn Neo - Sega SG-1000 Games': 'sg1000',
    'FinalBurn Neo - SuprGrafx Games': 'sgx',
    'FinalBurn Neo - TurboGrafx 16 Games': 'tg16',
    'FinalBurn Neo - ZX Spectrum Games': 'spectrum',
}

class FbneoDat(XMLDatFile):
    seed: str = 'nointro'

    def initial_parse(self) -> list:
        """ Parse the dat file. """
        # pylint: disable=R0801
        self.preffix = 'Arcade'
        self.company = 'FinalBurnNeo/roms'
        self.system = systems.get(self.name, 'unknown')
        self.suffix = ''
        self.date = ''

        return [self.preffix, self.company, self.system, self.suffix, self.date]
