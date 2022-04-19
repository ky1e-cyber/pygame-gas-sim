import pygame, sys, random, math
from pygame.locals import *

random.seed()



pygame.init()
clock = pygame.time.Clock()
W_SIZE = (1600, 900)
screen = pygame.display.set_mode(W_SIZE, 0, 32)
display_surf = pygame.Surface((960, 540))

TILE_SIZE = 1
CONT_SIZE = (601, 501)
collider_origin = (10, 10)

sq_v = 58.8
m = 1.6 * (10**(-27))

mol_list = []

def constrain(value, minv, maxv):
    return min(max(minv, value), maxv)

def cont_collider(origin:tuple, size:tuple) -> tuple: ## 0 - top, 1 - bottom, 2 - left, 3 - right
    cont = [0, 0, 0, 0]
    cont[0] = pygame.Rect(origin, (size[0] * TILE_SIZE, TILE_SIZE))
    cont[1] = pygame.Rect(origin[0], origin[1] + TILE_SIZE * size[1], size[0] * TILE_SIZE, TILE_SIZE)
    cont[2] = pygame.Rect(origin, (TILE_SIZE, TILE_SIZE * size[1]))
    cont[3] = pygame.Rect(origin[0] + TILE_SIZE * size[0], origin[1], TILE_SIZE, TILE_SIZE * size[1])
    return tuple(cont)

def cont_render(rect_tuple:tuple, color, surface:pygame.Surface):
    for rect in rect_tuple:
        pygame.draw.rect(surface, color, rect)


container = cont_collider(collider_origin, CONT_SIZE)
container_center_x = container[2].x + TILE_SIZE + ((TILE_SIZE * CONT_SIZE[0]) // 2)

SORT_RES = 32
sorted_mol_lists = [[] for i in range(SORT_RES + 2)]
sort_size = ((container[3].x - TILE_SIZE) - (container[2].x + TILE_SIZE)) / SORT_RES

class Molecule():
    def __init__(self, x, y, velo_scalar, angle, mass:float, color:tuple = (0, 0, 0)):
        self.rectangle = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.mass = mass
        self.velocity = pygame.math.Vector2((velo_scalar, 0)).rotate(angle)
        self.color:tuple = color
    def render(self, surface:pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rectangle)
    def tick(self, time:float):
        ## For X
        self.rectangle.x = (self.rectangle.x + self.velocity[0] * time)
        if (self.rectangle.x <= (container[2].x + TILE_SIZE)):
            self.rectangle.x = 2 * (container[2].x + TILE_SIZE) - self.rectangle.x
            self.velocity[0] *= -1
        elif (self.rectangle.x >= (container[3].x - TILE_SIZE)):
            self.rectangle.x = 2 * (container[3].x - TILE_SIZE) - self.rectangle.x
            self.velocity[0] *= -1
        ## For Y
        self.rectangle.y = (self.rectangle.y + self.velocity[1] * time)
        if (self.rectangle.y <= (container[0].y + TILE_SIZE)):
            self.rectangle.y = 2 * (container[0].y + TILE_SIZE) - self.rectangle.y
            self.velocity[1] *= -1
        elif (self.rectangle.y >= (container[1].y - TILE_SIZE)):
            self.rectangle.y = 2 * (container[1].y - TILE_SIZE) - self.rectangle.y
            self.velocity[1] *= -1
        ## Sorted List
        ind = int((self.rectangle.x - (container[2].x + TILE_SIZE)) // sort_size)
        if (ind < 0) or (ind > (sort_size - 1)):
            return
        collision_check(sorted_mol_lists[ind], self)
        sorted_mol_lists[ind].append(self)


def collision_check(sorted_list:list, mol:Molecule):
    for mol_check in sorted_list:
        if ((mol_check.rectangle.x - mol.rectangle.x) ** 2 + (mol_check.rectangle.y - mol.rectangle.y) ** 2 == TILE_SIZE ** 2):
            ## Resolve collision
            ## Unit vectors (tangential and normal)
            un = pygame.math.Vector2((mol_check.rectangle.x - mol.rectangle.x, mol_check.rectangle.y - mol.rectangle.y)).normalize()
            ut = pygame.math.Vector2(un[1] * -1, un[0])

            ## Velocity scalars for first (mol)
            sc_vn1 = un * mol.velocity
            sc_vt1 = ut * mol.velocity

            ## Velocity scalars for second (mol_check)
            sc_vn2 = un * mol_check.velocity
            sc_vt2 = ut * mol_check.velocity

            ## New scalars
            sc_vn1 = (sc_vn1 * (mol.mass - mol_check.mass) + 2 * mol_check.mass * sc_vn2) / (mol.mass + mol_check.mass)
            sc_vn2 = (sc_vn2 * (mol_check.mass - mol.mass) + 2 * mol.mass * sc_vn1) / (mol.mass + mol_check.mass)

            ## Resolve vectors for objects
            mol.velocity = (sc_vn1 * un) + (sc_vt1 * ut)
            mol_check.velocity = (sc_vn2 * un) + (sc_vt2 * ut)


for j in range(500):
    mol_list.append(Molecule(random.randint(container[2].x + TILE_SIZE, container[3].x - TILE_SIZE), random.randint(container[0].y + TILE_SIZE, container[1].y - TILE_SIZE), sq_v, random.randint(0, 360), m))


while True:
    delta_time = clock.tick(30) / 100
    display_surf.fill((146,244,255))
    cont_render(container, (0, 180, 46), display_surf)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    sorted_mol_lists = [[] for i in range(SORT_RES + 2)]
    for mol in mol_list:
        mol.tick(delta_time)
        mol.render(display_surf)
    pygame.transform.scale(display_surf, W_SIZE, screen)
    pygame.display.update()

def run():
    while True:
        delta_time = clock.tick(30) / 100
        display_surf.fill((146,244,255))
        cont_render(container, (0, 180, 46), display_surf)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
        sorted_mol_lists = [[] for i in range(SORT_RES + 2)]
        for mol in mol_list:
            mol.tick(delta_time)
            mol.render(display_surf)
        pygame.transform.scale(display_surf, W_SIZE, screen)
        pygame.display.update()


if __name__ == "__main__":
    run()
    pygame.quit()
    sys.exit()
