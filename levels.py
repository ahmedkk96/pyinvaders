import gameobjects


class EnemyTemplate:
    def __init__(self, enemy, mover, shooter):
        self.mover = mover
        self.shooter = shooter
        self.enemy = enemy

    def setup(self):
        self.shooter.set_child(self.enemy)
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

    def create_wave(wave_number, player):
        """
        Creates wave based on predefined waves,

        :param wave_number: Wave index (starting from 1)

        :returns: tuple (wave, singles)
        """

        enemy_group_temp = None
        enemy_singles = []

        enemy_singles = []

        if wave_number == 1:
            egt = Waves._create_classic_group()
            egt.enemy.uniform_rectangle(7, 3, gameobjects.Enemy)
            egt.setup()
            enemy_group_temp = egt
        elif wave_number == 2:
            egt = Waves._create_classic_group()
            egt.enemy.mixed_rows(7,
                                 [gameobjects.Enemy] * 3 +
                                 [gameobjects.Enemy2])
            egt.setup()
            enemy_group_temp = egt
        elif wave_number == 3:
            for x in range(0, 4):
                enemy = gameobjects.EnemyTargtedBullet(player)
                pos = (200 + x * 200, 300)
                enemy.set_pos(pos)
                move = gameobjects.MovementLinear(1, pos,
                                                  (pos[0]+200, pos[1]))
                move.set_child(enemy)
                move.loop = True
                shoot = gameobjects.ShooterPeriodic()
                shoot.set_interval(2)
                shoot.set_child(enemy)
                enemy_singles.append(EnemyTemplate(enemy,
                                                   move,
                                                   shoot))

        return (enemy_group_temp, enemy_singles)
