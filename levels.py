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

    def _create_classic_group():
            mover = gameobjects.MovmentClassic()
            shooter = gameobjects.ShooterPeriodic()
            enemy_group = gameobjects.EnemyRect()
            return EnemyTemplate(enemy_group,
                                 mover,
                                 shooter)

    def wave_1(player):
        egt = Waves._create_classic_group()
        egt.enemy.set_pos((200, 100))
        egt.enemy.uniform_rectangle(7, 3, gameobjects.Enemy)
        egt.setup()
        return [egt]

    def wave_2(player):
        egt = Waves._create_classic_group()
        egt.enemy.mixed_rows(7, [gameobjects.Enemy] * 3 +
                                [gameobjects.Enemy2])
        # egt.mover.speed_x *= 1.4
        egt.setup()
        return [egt]

    def wave_3(player):
        eg = gameobjects.EnemyGroup()
        for x in range(0, 4):
            enemy = gameobjects.EnemyTargtedBullet(player)
            pos = (200 + x * 200, 100)
            enemy.set_pos(pos)
            eg.append(enemy)

        pos = eg.get_pos()
        move = gameobjects.MovementLinear(1, (pos.x, pos.y),
                                          (pos.x+200, pos.y))
        move.loop = True
        shoot = gameobjects.ShooterPeriodic()
        shoot.set_interval(0.5)
        egt = EnemyTemplate(eg, move, shoot)
        egt.setup()
        return [egt]

    def wave_4(player):
        eg, es = Waves.wave_5(player)
        es.enemy.on_removed_event.remove(es.mover.on_child_removed)
        es.mover = None
        return [eg, es]

    def wave_5(player):
        es = Waves.wave_3(player)
        eg = Waves.wave_2(player)
        pos = eg[0].enemy.get_pos()
        pos.y += 150
        eg[0].enemy.set_pos(pos)
        eg[0].mover.set_child(eg[0].enemy)
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

        return wave_list[wave_number-1](player)
