import pygame
from PIL import Image
import random
import requests

session = "7fcd9b45-0842-4174-8cfa-4d4f186b4eef"
BASE_API = "https://roverdata2-production.up.railway.app"
direction = 0
# Constants888
GRID_SIZE = 10
CELL_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
EMPTY = 0
OBSTACLE = 1
HUMAN = 2
DIRECTIONS = ['right', 'down', 'left', 'up']
EMPTY_COLOR = (255, 255, 255)
OBSTACLE_COLOR = (0, 0, 0)
HUMAN_COLOR = (0, 255, 0)
MARK_COLOR = (255, 0, 0)
def charge():
    response = requests.post(f"{BASE_API}/api/rover/charge?session_id={session}")
    data = response.json()
    return data.get("message")
def get_sensor_data():
    response = requests.get(f"{BASE_API}/api/rover/sensor-data?session_id={session}")
    print(response.json())
    return response.json()

def move(direction):
    response = requests.post(f"{BASE_API}/api/rover/move?session_id={session}&direction={direction}")
    print(response.json().get("message"))
    return response.json().get("message")

def load_gif(filename):
    pil_image = Image.open(filename)
    frames = []
    for frame in range(pil_image.n_frames):
        pil_image.seek(frame)
        frame_surface = pygame.image.fromstring(
            pil_image.tobytes(), pil_image.size, pil_image.mode
        ).convert_alpha()
        frame_surface = pygame.transform.scale(frame_surface, (CELL_SIZE, CELL_SIZE))
        frames.append(frame_surface)
    return frames

def create_grid():
    grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for _ in range(10):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        grid[y][x] = OBSTACLE
    for _ in range(5):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[y][x] == EMPTY:
                grid[y][x] = HUMAN
                break
    return grid

def find_nearest_human(rover_x, rover_y, grid):
    humans = [(x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE) if grid[y][x] == HUMAN]
    if not humans:
        return None
    return min(humans, key=lambda h: abs(h[0] - rover_x) + abs(h[1] - rover_y))

def navigate_to_human(rover_x, rover_y, human_x, human_y):
    if rover_x < human_x:
        
        return 0  # Move right
    elif rover_x > human_x:
        
        return 2  # Move left
    elif rover_y < human_y:
        
        return 1  # Move down
    elif rover_y > human_y:
        
        return 3  # Move up
    return None

def draw_grid(grid, rover_x, rover_y, humans_tagged, rover_frames, rover_frame_index):
    screen.fill(EMPTY_COLOR)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == OBSTACLE:
                pygame.draw.rect(screen, OBSTACLE_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif grid[y][x] == HUMAN:
                pygame.draw.rect(screen, HUMAN_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for human in humans_tagged:
        mark_x = human[0] * CELL_SIZE + CELL_SIZE // 2
        mark_y = human[1] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, MARK_COLOR, (mark_x, mark_y), 5)
    rover_frame = rover_frames[rover_frame_index]
    screen.blit(rover_frame, (rover_x * CELL_SIZE, rover_y * CELL_SIZE))
    pygame.display.flip()
def move_forward(x, y, direction):
    """Move the rover forward in its current direction."""
    if direction == 0:  # right
        move("right")
        return min(x+1, GRID_SIZE-1), y
    elif direction == 1:  # down
        move("backward")
        return x, min(y+1, GRID_SIZE-1)
    elif direction == 2:  # left
        move("left")
        return max(x-1, 0), y
    elif direction == 3:  # up
        move("forward")
        return x, max(y-1, 0)
    return x, y


def run_simulation():
    
    pygame.init()
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rescue Rover Simulation")
    
    rover_frames = load_gif("rover.gif")
    sensor_info = get_sensor_data()
    rover_x, rover_y = sensor_info["position"]["x"] // CELL_SIZE, sensor_info["position"]["y"] // CELL_SIZE
    grid = create_grid()
    humans_tagged = []
    rover_frame_index = 0
    clock = pygame.time.Clock()
    running = True
    
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        sensor_info = get_sensor_data()
        if sensor_info['battery_level'] <= 10:
            print(charge())
        if sensor_info["rfid"]["tag_detected"]:
            human = find_nearest_human(rover_x, rover_y, grid)
            if human:
                direction = navigate_to_human(rover_x, rover_y, *human)
                if direction is not None:
                    move(DIRECTIONS[direction])
                    if direction == 0:
                        move("right")
                        rover_x += 1
                    elif direction == 1:
                        move("forward")
                        rover_y += 1
                    elif direction == 2:
                        move("left")
                        rover_x -= 1
                    elif direction == 3:
                        move("backword")
                        rover_y -= 1
                    if (rover_x, rover_y) == human:
                        grid[rover_y][rover_x] = EMPTY
                        humans_tagged.append(human)
        else:
            direction = 0
            move_forward(rover_x, rover_y, direction)                      
        if sensor_info["ultrasonic"]["detection"]:
            print("Obstacle detected. Stopping navigation.")
            break
        
        draw_grid(grid, rover_x, rover_y, humans_tagged, rover_frames, rover_frame_index)
        rover_frame_index = (rover_frame_index + 1) % len(rover_frames)
        clock.tick(5)
    
    pygame.quit()

if __name__ == "__main__":
    run_simulation()