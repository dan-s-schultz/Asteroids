from tkinter import *
from Game import *
from geometry import Point2D, Vector2D
import math
import random
import time

TIME_STEP = 0.5

class MovingBody(Agent):

    def __init__(self, p0, v0, world):
        self.velocity = v0
        self.accel    = Vector2D(0.0,0.0)
        Agent.__init__(self,p0,world)

    def color(self):
        return "#000080"

    def shape(self):
        p1 = self.position + Vector2D( 0.125, 0.125)       
        p2 = self.position + Vector2D(-0.125, 0.125)        
        p3 = self.position + Vector2D(-0.125,-0.125)        
        p4 = self.position + Vector2D( 0.125,-0.125)
        return [p1,p2,p3,p4]

    def steer(self):
        return Vector2D(0.0)

    def update(self):
        self.position = self.position + self.velocity * TIME_STEP
        self.velocity = self.velocity + self.accel * TIME_STEP
        self.accel    = self.steer()
        self.world.trim(self)
        
class Dockable(MovingBody):
  
    WORTH     = 50
    MIN_SPEED = 0.1
    MAX_SPEED = 0.3
    SIZE      = 2.0
    
    def __init__(self,world):
        world.number_of_asteroids += 1
        self.radius = self.SIZE
        velocity0 = self.choose_velocity()
        position0 = world.bounds.point_at(random.random(),random.random())
        if abs(velocity0.dx) >= abs(velocity0.dy):
            if velocity0.dx > 0.0:
                # LEFT SIDE
                position0.x = world.bounds.xmin
            else:
                # RIGHT SIDE
                position0.x = world.bounds.xmax
        else:
            if velocity0.dy > 0.0:
                # BOTTOM SIDE
                position0.y = world.bounds.ymin
            else:
                # TOP SIDE
                position0.y = world.bounds.ymax
        MovingBody.__init__(self,position0,velocity0,world)
        self.sv = velocity0
        # self.sv is used to store ship velocity later.  It is init as v0 just to give it vector type
        self.make_shape()
  
    def color(self):
        return ("lawn green")

    def choose_velocity(self):
        return Vector2D.random() * random.uniform(self.MIN_SPEED,self.MAX_SPEED) 
        
    def make_shape(self):
        angle = 0.0
        dA = 2.0 * math.pi / 15.0
        center = Point2D(0.0,0.0)
        self.polygon = []
        for i in range(15):
            if i % 3 == 0 and random.random() < 0.2:
                r = self.radius/2.0 + random.random() * 0.25
            else:
                r = self.radius - random.random() * 0.25
            dx = math.cos(angle)
            dy = math.sin(angle)
            angle += dA
            offset = Vector2D(dx,dy) * r
            self.polygon.append(offset)

    def shape(self):
        return [self.position + offset for offset in self.polygon]

    def is_hit_by(self, docker):
        return ((self.position - docker.position).magnitude() <= self.radius)

    def update(self):
        MovingBody.update(self)
        ships = [a for a in self.world.agents if isinstance(a,Ship)]
        for s in ships:
          
          if s.docked == False and (s.is_hit_by(self)) and s.dock_mode == True:
          # ship is not docked and intercepts dockable body
          # s.docked designates whether or not the ship is docked, not whether or not the ship wishes to dock.
          # dockmode is changed by a keypress event
            s.docked = True
            self.sv = s.velocity
            s.position = self.position
            s.velocity = self.velocity
            return
          elif s.docked == True and (s.is_hit_by(self)) and s.dock_mode == True:
          # ship is docked and is staying that way
            s.position = self.position
            s.velocity = self.velocity
            return
          elif s.docked == True and (s.is_hit_by(self)) and s.dock_mode == False:
          # ship is docked on body and wants to leave
          # mildly change ship direction and give ship time to leave
              s.velocity = self.sv.over(2.0)
              s.docked = False


class Minable(Dockable):
  
    
    # ERROR on Ember class undefined...?
    # mining feature has issue that ship must undock for asteroid to leave world
    
    #SHRAPNEL_CLASS  = Ember
    SHRAPNEL_PIECES = 15
    WORTH           = 100
    
    def __init__(self,world):
        Dockable.__init__(self,world)
        self.flash_ctr = 0
        
    
    def explode(self):
    # This works but the ship has to undock before the asteroid is destroyed
        self.world.score += self.WORTH
        #for _ in range(self.SHRAPNEL_PIECES):
        #    self.SHRAPNEL_CLASS(self.position,self.world)
        print("I should explode!")
        self.leave()

    def color(self):
    # changes color of asteroid if it is being mined
      if   self.flash_ctr    == 0:
        return "DodgerBlue4"
      elif self.flash_ctr%10 == 0:
        return "orange red"
      else:
        return "DodgerBlue4"

    def update(self):
        MovingBody.update(self)
        ships = [a for a in self.world.agents if isinstance(a,Ship)]
        for s in ships:
          if s.docked == False and (s.is_hit_by(self)) and s.dock_mode == True:
          # ship is not docked and intercepts dockable body
          # s.docked designates whether or not the ship is docked, not whether or not the ship wishes to dock.
          # dockmode is changed by a keypress event
            s.docked   = True
            self.sv    = s.velocity
            s.position = self.position
            s.velocity = self.velocity
            return
          elif s.docked == True and (s.is_hit_by(self)) and s.dock_mode == True:
          # ship is docked and is staying that way
            s.position      = self.position
            s.velocity      = self.velocity
            self.flash_ctr += 1
            return
          elif s.docked == True and (s.is_hit_by(self)) and s.dock_mode == False:
          # ship is docked on body and wants to leave, it leaves here
              s.velocity = self.sv.over(2.0)
              s.docked   = False
          break
        if self.flash_ctr > 100:
        # ship has mined asteroid, destroy asteroid, free ship
            self.explode()


#class Dock(Dockable):
  
    # copy init function from dockable
    # shape of Dock will be rectangular
    # Game will begin and end with Dock
    # Dock should be invincible
    # when ship docks, dock displays an upgrade menu
    # when the state of the ship is docked on dock, we can use keypress events to buy upgrades
    # first we need points and a score display for the asteroids destroyed in the status bar.
    
    

class Shootable(MovingBody):

    SHRAPNEL_CLASS  = None
    SHRAPNEL_PIECES = 0
    WORTH           = 1

    def __init__(self, position0, velocity0, radius, world):
        self.radius = radius
        MovingBody.__init__(self, position0, velocity0, world)

    def is_hit_by(self, photon):
        return ((self.position - photon.position).magnitude() < self.radius)

    def explode(self):
        self.world.score += self.WORTH
        if self.SHRAPNEL_CLASS == None:
            return
        for _ in range(self.SHRAPNEL_PIECES):
            self.SHRAPNEL_CLASS(self.position,self.world)
        self.leave()

class Asteroid(Shootable):
    WORTH     = 5
    MIN_SPEED = 0.1
    MAX_SPEED = 0.3
    SIZE      = 3.0

    def __init__(self, position0, velocity0, world):
        Shootable.__init__(self,position0, velocity0, self.SIZE, world)
        self.make_shape()

    def choose_velocity(self):
        return Vector2D.random() * random.uniform(self.MIN_SPEED,self.MAX_SPEED) 
        
    def make_shape(self):
        angle = 0.0
        dA = 2.0 * math.pi / 15.0
        center = Point2D(0.0,0.0)
        self.polygon = []
        for i in range(15):
            if i % 3 == 0 and random.random() < 0.2:
                r = self.radius/2.0 + random.random() * 0.25
            else:
                r = self.radius - random.random() * 0.25
            dx = math.cos(angle)
            dy = math.sin(angle)
            angle += dA
            offset = Vector2D(dx,dy) * r
            self.polygon.append(offset)

    def shape(self):
        return [self.position + offset for offset in self.polygon]

class ParentAsteroid(Asteroid):
    def __init__(self,world):
        world.number_of_asteroids += 1
        velocity0 = self.choose_velocity()
        position0 = world.bounds.point_at(random.random(),random.random())
        if abs(velocity0.dx) >= abs(velocity0.dy):
            if velocity0.dx > 0.0:
                # LEFT SIDE
                position0.x = world.bounds.xmin
            else:
                # RIGHT SIDE
                position0.x = world.bounds.xmax
        else:
            if velocity0.dy > 0.0:
                # BOTTOM SIDE
                position0.y = world.bounds.ymin
            else:
                # TOP SIDE
                position0.y = world.bounds.ymax
        Asteroid.__init__(self,position0,velocity0,world)

    def explode(self):
        Asteroid.explode(self)
        self.world.number_of_asteroids -= 1

class Ember(MovingBody):
    INITIAL_SPEED = 2.0
    SLOWDOWN      = 0.2
    TOO_SLOW      = INITIAL_SPEED / 20.0

    def __init__(self, position0, world):
        velocity0 = Vector2D.random() * self.INITIAL_SPEED
        MovingBody.__init__(self, position0, velocity0, world)

    def color(self):
        white_hot  = "#FFFFFF"
        burning    = "#FF8080"
        smoldering = "#808040"
        speed = self.velocity.magnitude()
        if speed / self.INITIAL_SPEED > 0.5:
            return white_hot
        if speed / self.INITIAL_SPEED > 0.25:
            return burning
        return smoldering

    def steer(self):
        return -self.velocity.direction() * self.SLOWDOWN

    def update(self):
        MovingBody.update(self)
        if self.velocity.magnitude() < self.TOO_SLOW:
            self.leave()

class ShrapnelAsteroid(Asteroid):
    def __init__(self, position0, world):
        world.number_of_shrapnel += 1
        velocity0 = self.choose_velocity()
        Asteroid.__init__(self, position0, velocity0, world)

    def explode(self):
        Asteroid.explode(self)
        self.world.number_of_shrapnel -= 1

class SmallAsteroid(ShrapnelAsteroid):
    WORTH           = 20
    MIN_SPEED       = Asteroid.MIN_SPEED * 2.0
    MAX_SPEED       = Asteroid.MAX_SPEED * 2.0
    SIZE            = Asteroid.SIZE / 2.0
    SHRAPNEL_CLASS  = Ember
    SHRAPNEL_PIECES = 8

    def color(self):
        return "#A8B0C0"

class MediumAsteroid(ShrapnelAsteroid):
    WORTH           = 10
    MIN_SPEED       = Asteroid.MIN_SPEED * math.sqrt(2.0)
    MAX_SPEED       = Asteroid.MAX_SPEED * math.sqrt(2.0)
    SIZE            = Asteroid.SIZE / math.sqrt(2.0)
    SHRAPNEL_CLASS  = SmallAsteroid
    SHRAPNEL_PIECES = 3

    def color(self):
        return "#7890A0"

class LargeAsteroid(ParentAsteroid):
    SHRAPNEL_CLASS  = MediumAsteroid
    SHRAPNEL_PIECES = 2

    def color(self):
        return "#9890A0"

class Photon(MovingBody):
    INITIAL_SPEED = 2.0 * SmallAsteroid.MAX_SPEED
    LIFETIME      = 40
    # changing intial speed will result in a change of the range of your photon cannon
    # changing lifetime will change the range, but not the speed of the weapon

    def __init__(self,source,world):
        self.age  = 0
        v0 = source.velocity + (source.get_heading() * self.INITIAL_SPEED)
        MovingBody.__init__(self, source.position, v0, world)

    def color(self):
        return "#8080FF"

    def update(self):
        MovingBody.update(self)
        self.age += 1
        if self.age >= self.LIFETIME:
            self.leave()
        else:
            targets = [a for a in self.world.agents if isinstance(a,Shootable) and (not isinstance(a,Ship))]
            for t in targets:
                if(t.is_hit_by(self)):
                    t.explode()
                    self.leave()
                    return



class Ship(Shootable):
    TURNS_IN_360   = 24
    IMPULSE_FRAMES = 4
    ACCELERATION   = 0.05
    MAX_SPEED      = 2.0
    
    #explode ship
    SHRAPNEL_CLASS  = Ember
    SHRAPNEL_PIECES = 50
    
    # die
    SIZE = 3.0
    DEATH_DELAY = 50
    

    def __init__(self,world):
        position0    = Point2D()
        velocity0    = Vector2D(0.0,0.0)
        Shootable.__init__(self,position0,velocity0,self.SIZE,world)
        self.speed   = 0.0
        self.angle   = 90.0
        self.impulse = 0
        self.recent_death = False
        self.death_delay = self.DEATH_DELAY
        self.dock_mode = False
        self.docked = False

    def color(self):
        return "#F0C080"

    def get_heading(self):
        angle = self.angle * math.pi / 180.0
        return Vector2D(math.cos(angle), math.sin(angle))
        
    def turn_left(self):
        self.angle += 360.0 / self.TURNS_IN_360

    def turn_right(self):
        self.angle -= 360.0 / self.TURNS_IN_360

    def speed_up(self):
        self.impulse = self.IMPULSE_FRAMES

    def shoot(self):
        Photon(self, self.world)
    
    def shape(self):
        h  = self.get_heading()
        hp = h.perp()
        p1 = self.position + h * 2.0
        p2 = self.position + hp*0.3
        p3 = self.position + hp*0.7 - h*0.5
        p4 = self.position - h*0.2
        p5 = self.position - hp*0.7 - h*0.5
        p6 = self.position - hp*0.3
        return [p1,p2,p3,p4,p5,p6]

    def steer(self):
        if self.impulse > 0:
            self.impulse -= 1
            return self.get_heading() * self.ACCELERATION
        else:
            return Vector2D(0.0,0.0)

    def trim_physics(self):
        MovingBody.trim_physics(self)
        m = self.velocity.magnitude()
        if m > self.MAX_SPEED:
            self.velocity = self.velocity * (self.MAX_SPEED / m)
            self.impulse = 0

    def explode(self):
        if self.SHRAPNEL_CLASS == None:
            return
        for _ in range(self.SHRAPNEL_PIECES):
            self.SHRAPNEL_CLASS(self.position,self.world)

    def change_dockmode(self):
        if self.dock_mode == False:
          self.dock_mode = True
        else:
          self.dock_mode = False
      

    # maybe Ship should have its own leave method that inherits from leave, but changes life count
    def update(self):
        MovingBody.update(self)
        
        if self.recent_death == False:
          
          if self.world.lives <= 0:
          # end of game
          # some cool "GAME OVER" print screen would be nice
            self.explode()
            self.leave()
            self.world.report("GAME OVER, press 'q' to quit")
          # Needs to change GAME_OVER = True and say so
          else:
              targets = [a for a in self.world.agents if isinstance(a,Shootable)]
              for t in targets:
                  if ( (t is not self) and t.is_hit_by(self) ):
                      t.explode()
                      self.explode()
                      self.world.lives -= 1
                      life_report = "WATCH OUT! Lives = "+str(self.world.lives)
                      self.world.report()
                      self.world.report()
                      self.world.report()
                      self.world.report(life_report)
                      self.recent_death = True
                      self.death_delay = 200
                      break

                    
        if self.death_delay > 0:
            self.death_delay -= 1
        else:
            self.recent_death = False
            # death_delay gives the ship a moment of invincibility after striking an asteroid
                    # print to screen: number of lives
                    # need to pause game for a second and say DAMAGE SEVERE Lives = X
                    # reboot position, stop asteroid movement
                    # We could also destroy all small asteroids made by the impact, without subtracting lives?



# class Alien(Moving Body):

class PlayAsteroids(Game):

    DELAY_START      = 50
    MAX_ASTEROIDS    = 6
    INTRODUCE_CHANCE = 0.01
    
    def __init__(self):
        Game.__init__(self,"ASTEROIDS!!!",60.0,45.0,800,600,topology='wrapped')

        self.number_of_asteroids = 0
        self.number_of_shrapnel = 0
        self.level = 1
        self.score = 0
        self.lives = 3

        self.before_start_ticks = self.DELAY_START
        self.started = False

        self.ship = Ship(self)

    """
    attempting to get score reported when each thing leaves world, but score reports multiple times...
    right now score report is just in terminal. It can easily be made otherwise (as I've done with the pause_edit file)
    Lives report is handled in ship.  We can do the same thing inside of the "explode()" function for all asteroids!
    
    def remove(self, agent):
        self.agents.remove(agent)
        score_report = "Points = "+str(self.score)
        self.report(score_report)"""

    def max_asteroids(self):
        return min(2 + self.level,self.MAX_ASTEROIDS)

    def handle_keypress(self,event):
        Game.handle_keypress(self,event)
        if event.char == 'i':
            self.ship.speed_up()
        elif event.char == 'j':
            self.ship.turn_left()
        elif event.char == 'l':
            self.ship.turn_right()
        elif event.char == 'e':
        # later on we may switch the cause of this event to an asteroid impact
            self.ship.explode()
        elif event.char == ' ':
            self.ship.shoot()
        if event.char == 'd':
            self.ship.change_dockmode()
        
        
    def update(self):

        # Are we waiting to toss asteroids out?
        if self.before_start_ticks > 0:
            self.before_start_ticks -= 1
        else:
            self.started = True
        
        # Should we toss a new asteroid out?
        if self.started:
            tense = (self.number_of_asteroids >= self.max_asteroids())
            tense = tense or (self.number_of_shrapnel >= 2*self.level)
            if not tense and random.random() < self.INTRODUCE_CHANCE:
                LargeAsteroid(self)
                Minable(self)

        Game.update(self)
        

print("Hit 'j' and 'l' to turn, 'i' to create thrust, and SPACE to shoot.")
print("Press 'q' to quit, and 'p' to pause.")
game = PlayAsteroids()
# can we add music to the game?  Some synthwave jams?
while not game.GAME_OVER:
  # while not PAUSE_GAME:
    time.sleep(1.0/60.0)
    game.update()
