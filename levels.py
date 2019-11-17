import gameobjects


class EnemyTemplate:
    def __init__(self, enemy, mover, shooter):
        self.mover = mover
        self.shooter = shooter
        self.enemy = enemy

    def setup(self):
        if self.shooter is not None:
            self.shooter.set_child(self.enemy)
        if self.mover is not None:
            self.mover.set_child(self.enemy)


class Waves:
    '''
    Static structure for holding waves information,
    '''

    def _classic_group():
        mover = gameobjects.MovmentClassic()
        egt = Waves._static_group()
        egt.mover = mover
        return egt

    def _static_group():
        shooter = gameobjects.ShooterPeriodic()
        enemy_group = gameobjects.EnemyRect()
        return EnemyTemplate(enemy_group,
                             None,
                             shooter)

    def _enemy_at(pos, type, *params):
        enemy = type(*params)
        enemy.set_pos(pos)
        return enemy

    def _join_enemies(enemies):
        eg = gameobjects.EnemyGroup()
        for e in enemies:
            eg.append(e)

        return eg

    def wave_1(player):
        egt = Waves._classic_group()
        egt.enemy.uniform_rectangle(7, 3, gameobjects.Enemy)
        egt.enemy.center_hor()
        egt.enemy.set_top(100)
        egt.setup()
        return [egt]

    def wave_2(player):
        egt = Waves._classic_group()
        egt.enemy.mixed_rows(7, [gameobjects.Enemy] * 3 +
                                [gameobjects.Enemy2])
        egt.enemy.center_hor()
        egt.enemy.set_top(100)
        egt.setup()
        return [egt]

    def wave_3(player):
        eg = gameobjects.EnemyGroup()
        for x in range(0, 4):
            enemy = Waves._enemy_at((x * 200, 0),
                                    gameobjects.EnemyTargtedBullet, player)
            eg.append(enemy)

        eg.center_hor()
        eg.set_top(100)
        move = gameobjects.MovementLinear(1.5, (-100, 0),
                                          (100, 0))
        move.loop = True
        shoot = gameobjects.ShooterPeriodic()
        shoot.set_interval(0.5)
        egt = EnemyTemplate(eg, move, shoot)
        egt.setup()
        return [egt]

    def wave_4(player):
        eg, es = Waves.wave_5(player)
        es.mover.unset_child()
        es.mover = None
        return [eg, es]

    def wave_5(player):
        es = Waves.wave_3(player)
        eg = Waves.wave_2(player)
        eg[0].enemy.set_top(150)
        eg[0].mover.speed_x = 150
        eg[0].mover.step_y = 0

        return eg + es

    def wave_6(player):
        meteorgen = gameobjects.MeteorGenerator(60)
        return [EnemyTemplate(meteorgen, None, None)]

    def create_wave(wave_number, player):
        """
        Creates wave based on predefined waves,

        :param wave_number: Wave index (starting from 1)

        :returns: tuple (wave, singles)
        """
        wave_list = [Waves.wave_1, Waves.wave_2,
                     Waves.wave_3, Waves.wave_4,
                     Waves.wave_5, Waves.wave_6]

        if wave_number > len(wave_list):
            return []
        return wave_list[wave_number-1](player)
