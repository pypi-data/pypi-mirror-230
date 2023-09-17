from itertools import product

import gymnasium as gym
import numpy as np

from craft2d.render.render import HumanRenderer, RgbRenderer

RIGHT = 0
LEFT = 1
UP = 2
DOWN = 3
INTERACT = 4

MAX_RESOURCE_COUNT = 10
RESOURCE_COUNTS = {
    "tree": 12,
    "stone": 12,
    "grass": 12,
    "gem": 1,
}
ENVIRONMENT_OBJECTS = (
    "tree",
    "stone",
    "grass",
    "crafting-table",
    "water",
    "gem",
    "bridge",
    "princess",
)
INVENTORY_OBJECTS = (
    "wood",
    "stone",
    "grass",
    "sticks",
    "rope",
    "bridge",
    "weapon-basic",
    "gem",
    "weapon-advanced",
)
TASKS = {
    "get-wood": 0,
    "get-stone": 1,
    "get-grass": 2,
    "make-sticks": 3,
    "make-rope": 4,
    "make-bridge": 5,
    "make-basic-weapon": 6,
    "get-gem": 7,
    "make-advanced-weapon": 8,
}
PROPS = (
    "WD",
    "STN",
    "GRS",
    "STKS",
    "RP",
    "BRG",
    "W-BSC",
    "GEM",
    "W-ADV",
)


class Craft2dEnv(gym.Env):
    def __init__(
        self,
        n_rows: int,
        n_cols: int,
        render_mode: str = "human",
    ):
        super().__init__()
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.render_mode = render_mode
        self.n_env_objects = len(ENVIRONMENT_OBJECTS)
        self.n_inv_objects = len(INVENTORY_OBJECTS)

        self.action_space = gym.spaces.Discrete(5)

        # Oservation space is a tuple of: (environment, inventory, direction)
        self.observation_space = gym.spaces.Tuple(
            spaces=(
                gym.spaces.Box(
                    low=0,
                    high=max(self.n_rows, self.n_cols),
                    shape=(2,),
                ),
                gym.spaces.Box(
                    low=0,
                    high=MAX_RESOURCE_COUNT,
                    shape=(self.n_inv_objects,),
                ),
                gym.spaces.Box(
                    low=0,
                    high=1,
                    shape=(4,),
                ),
            )
        )
        self.reward_range = (0, 1)

        self.init_required = True

        if self.render_mode == "human":
            self.renderer = HumanRenderer(
                n_rows=self.n_rows,
                n_cols=self.n_cols,
                env_objects=ENVIRONMENT_OBJECTS,
                inv_objects=INVENTORY_OBJECTS,
                fps=24,
            )
        elif self.render_mode == "rgb_array":
            self.renderer = RgbRenderer(
                n_rows=self.n_rows,
                n_cols=self.n_cols,
                env_objects=ENVIRONMENT_OBJECTS,
                inv_objects=INVENTORY_OBJECTS,
            )

    def reset(
        self,
        seed: int = None,
        options: dict[str, str] = {
            "task_object": "WD",
            "task_object_count": "M1",
        },
    ):
        super().reset(seed=seed)
        np.random.seed(seed)
        # Reset number of steps taken in environment
        self.n_steps = 0

        # Reset task state
        self.task_object = options["task_object"]
        self.task_object_count = options["task_object_count"]
        self.task_set = False
        self.task_completed = False
        self.task_failed = False

        # Object order specified in ENVIRONMENT_OBJECTS
        self.grid = np.zeros((self.n_rows, self.n_cols, self.n_env_objects))
        # Object order specified in INVENTORY_OBJECTS
        self.inventory = np.zeros((self.n_inv_objects,))

        # Initialize agent position and direction
        self.agent_position = (0, 0)
        self.direction = np.zeros((4,))

        if self.init_required:
            self.init_required = False

            # Add resources to environment
            self._initialize_environment()
            self.cached_grid = self.grid.copy()
        else:
            self.grid = self.cached_grid.copy()

        # Setup island
        self._initialize_island()

        self.interaction_props = ()
        return self._create_observation()

    def step(self, action: int):
        self.interaction_props = ()

        if action == INTERACT:
            self._handle_interact_action()
        else:
            self._update_agent_position(action)
            self._update_agent_direction(action)

        obs = self._create_observation()
        reward = 0

        # Reward = 1 when agent interacts with princess while holding task object
        props = obs[-1]
        if props == ("P",) and self.task_object is not None:
            task_obj_idx = PROPS.index(self.task_object)

            if self.task_object_count == "M1":
                count = 1
            elif self.task_object_count == "M2":
                count = 2
            elif self.task_object_count == "M3":
                count = 3
            elif self.task_object_count == "M4":
                count = 4
            elif self.task_object_count == "M5":
                count = 5

            if self.inventory[task_obj_idx] == count:
                reward = 1
                self.task_completed = True

        done = reward == 1
        return obs, reward, done, False, {}

    def render(self):
        if self.render_mode is None:
            assert self.spec is not None
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You can specify the render_mode at initialization, "
                f'e.g. gym.make("{self.spec.id}", render_mode="rgb_array")'
            )
            return

        if self.render_mode in ("human", "rgb_array"):
            return self.renderer.render(
                grid=self.grid,
                inventory=self.inventory,
                agent_position=self.agent_position,
                direction=self.direction,
                quest_set=self.task_set,
                quest_object=self.task_object,
                quest_object_count=self.task_object_count,
                completed=self.task_completed,
                failed=self.task_failed,
            )

    def _create_observation(self):
        # Fill observation with out of bounds
        obs_grid = np.full((3, 3), fill_value=-1)

        for d_r, d_c in product(range(-1, 2), range(-1, 2)):
            n_r = self.agent_position[0] + d_r
            n_c = self.agent_position[1] + d_c

            # Test if out of bounds
            if (n_r >= self.n_rows or n_r < 0) or (n_c >= self.n_cols or n_c < 0):
                continue

            if np.max(self.grid[n_r, n_c]) == 0:
                # Empty cell
                obs_grid[d_r + 1, d_c + 1] = 0
            else:
                # Object
                obs_grid[d_r + 1, d_c + 1] = np.argmax(self.grid[n_r, n_c]) + 1

        if self.task_object is None:
            task_collected = np.array([0])
        else:
            task_collected = np.array([1])

        return (
            np.array([self.agent_position[0], self.agent_position[1]]).copy(),
            obs_grid.copy(),
            self.direction.copy(),
            # task_collected,
            self.interaction_props,
        )

    def _sample_position(self):
        row = np.random.randint(2, self.n_rows - 2)
        col = np.random.randint(2, self.n_cols - 2)
        return row, col

    def _initialize_environment(self):
        used_positions = []

        for i, object_name in enumerate(ENVIRONMENT_OBJECTS):
            if object_name in ("water", "bridge"):
                continue

            if object_name in RESOURCE_COUNTS:
                count = RESOURCE_COUNTS[object_name]
            else:
                count = 1

            # print(object_name)

            # center_row = np.random.randint(2, self.n_rows - 4)
            # center_col = np.random.randint(2, self.n_cols - 4)

            if object_name == "tree":
                center_row = 4
                center_col = 10
            elif object_name == "stone":
                center_row = 10
                center_col = 3
            elif object_name == "grass":
                center_row = 10
                center_col = 10
            elif object_name == "princess":
                center_row = 0 + 2
                center_col = 3 + 2
            elif object_name == "crafting-table":
                center_row = 0 + 2
                center_col = 6 + 2
            elif object_name == "gem":
                center_row = 3 + 2
                center_col = 3 + 2

            counter = 0

            for d_r, d_c in product(range(-2, 2), range(-2, 2)):
                if counter == count:
                    break

                if (center_row + d_r, center_col + d_c) in used_positions:
                    continue

                used_positions.append((center_row + d_r, center_col + d_c))
                self.grid[center_row + d_r, center_col + d_c, i] = 1
                counter += 1

    def _initialize_island(self):
        # Get island position
        for r, c in product(range(self.n_rows), range(self.n_cols)):
            if self.grid[r, c, ENVIRONMENT_OBJECTS.index("gem")] == 1:
                island_row = r
                island_col = c
                break

        # Surround island with water
        for d_r, d_c in product(range(-1, 2), range(-1, 2)):
            n_r = island_row + d_r
            n_c = island_col + d_c

            if (
                (n_r == r and n_c == c)
                or (n_r >= self.n_rows or n_r < 0)
                or (n_c >= self.n_cols or n_c < 0)
            ):
                continue

            self.grid[n_r, n_c, ENVIRONMENT_OBJECTS.index("water")] = 1

    def _update_agent_position(self, action: int):
        self.last_position = self.agent_position
        row, col = self.agent_position

        if action == RIGHT:
            n_row = row
            n_col = col + 1 if col + 1 < self.n_cols else col
        elif action == LEFT:
            n_row = row
            n_col = col - 1 if col - 1 >= 0 else col
        elif action == UP:
            n_row = row - 1 if row - 1 >= 0 else row
            n_col = col
        elif action == DOWN:
            n_row = row + 1 if row + 1 < self.n_rows else row
            n_col = col

        # Update position if no collision or water
        if np.max(self.grid[n_row, n_col]) == 0:
            self.agent_position = (n_row, n_col)

        # Allow agent to cross water if bridge has been placed
        object_type = np.argmax(self.grid[n_row, n_col])
        object_name = ENVIRONMENT_OBJECTS[object_type]

        if object_name == "bridge":
            self.agent_position = (n_row, n_col)

    def _update_agent_direction(self, action: int):
        last_direction = self.direction
        self.direction = np.zeros((4,))

        if action == RIGHT:
            self.direction[0] = 1
        elif action == LEFT:
            self.direction[1] = 1
        elif action == UP:
            self.direction[2] = 1
        elif action == DOWN:
            self.direction[3] = 1
        elif action == INTERACT:
            self.direction = last_direction

    def _handle_interact_action(self):
        # Cell in front of agent
        itr_row, itr_col = self._get_interaction_cell()

        # Test if cell is empty
        if np.max(self.grid[itr_row, itr_col]) == 0:
            return

        # Get object type
        object_type = np.argmax(self.grid[itr_row, itr_col])
        object_name = ENVIRONMENT_OBJECTS[object_type]

        if object_name == "princess":
            if not self.task_set:
                self.interaction_props = (self.task_object, self.task_object_count)
                self.task_set = True
            else:
                self.interaction_props = ("P",)
        elif self.task_object is None:
            # Cannot interact before task specified
            return

        # Collect resources from environment
        if object_name == "tree":
            self._collect_tree(itr_row, itr_col)
            self.interaction_props = ("WD", "CL")
        elif object_name == "stone":
            self._collect_stone(itr_row, itr_col)
            self.interaction_props = ("STN", "CL")
        elif object_name == "grass":
            self._collect_grass(itr_row, itr_col)
            self.interaction_props = ("GRS", "CL")
        elif object_name == "gem":
            self._collect_gem(itr_row, itr_col)
            self.interaction_props = ("GM", "CL")
        elif object_name == "water":
            self._handle_water_interaction(itr_row, itr_col)
        elif object_name == "crafting-table":
            self._handle_crafting_interaction()

    def _handle_crafting_interaction(self):
        if self.inventory[6] > 0 and self.inventory[7] > 0:
            # Advanced weapon
            self.inventory[8] += 1
            self.inventory[6] -= 1
            self.inventory[7] -= 1
            self.interaction_props = ("W-ADV", "CL")
        if self.inventory[3] > 0 and self.inventory[1] >= 2:
            # Weapon
            self.inventory[6] += 1
            self.inventory[3] -= 1
            self.inventory[1] -= 2
            self.interaction_props = ("W-BSC", "CL")
        elif self.inventory[3] > 0 and self.inventory[4] >= 1:
            # Bridge
            self.inventory[5] += 1
            self.inventory[3] -= 1
            self.inventory[4] -= 1
            self.interaction_props = ("BRG", "CL")
        elif self.inventory[0] > 1:
            # Sticks
            self.inventory[0] -= 2
            self.inventory[3] += 1
            self.interaction_props = ("STKS", "CL")
        elif self.inventory[2] > 1:
            # Rope
            self.inventory[2] -= 2
            self.inventory[4] += 1
            self.interaction_props = ("RP", "CL")

    def _handle_water_interaction(self, itr_row, itr_col):
        # Place bridge on water if agent has bridge in inventory
        water_idx_env = ENVIRONMENT_OBJECTS.index("water")
        bridge_idx_env = ENVIRONMENT_OBJECTS.index("bridge")
        bridge_idx_inv = INVENTORY_OBJECTS.index("bridge")

        if self.inventory[bridge_idx_inv] > 0:
            self.grid[itr_row, itr_col, bridge_idx_env] = 1
            self.grid[itr_row, itr_col, water_idx_env] = 0
            self.inventory[bridge_idx_inv] -= 1

    def _collect_tree(self, itr_row, itr_col):
        tree_idx_env = ENVIRONMENT_OBJECTS.index("tree")
        wood_idx_inv = INVENTORY_OBJECTS.index("wood")
        self.inventory[wood_idx_inv] += 1
        self.grid[itr_row, itr_col, tree_idx_env] = 0

    def _collect_stone(self, itr_row, itr_col):
        stone_idx_env = ENVIRONMENT_OBJECTS.index("stone")
        stone_idx_inv = INVENTORY_OBJECTS.index("stone")
        self.inventory[stone_idx_inv] += 1
        self.grid[itr_row, itr_col, stone_idx_env] = 0

    def _collect_grass(self, itr_row, itr_col):
        grass_idx_env = ENVIRONMENT_OBJECTS.index("grass")
        grass_idx_inv = INVENTORY_OBJECTS.index("grass")
        self.inventory[grass_idx_inv] += 1
        self.grid[itr_row, itr_col, grass_idx_env] = 0

    def _collect_gem(self, itr_row, itr_col):
        gem_idx_env = ENVIRONMENT_OBJECTS.index("gem")
        gem_idx_inv = INVENTORY_OBJECTS.index("gem")
        self.inventory[gem_idx_inv] += 1
        self.grid[itr_row, itr_col, gem_idx_env] = 0

    def _get_interaction_cell(self):
        interaction_row = self.agent_position[0]
        interaction_col = self.agent_position[1]

        if self.direction[0] == 1:
            interaction_col += 1 if interaction_col + 1 < self.n_cols else 0
        elif self.direction[1] == 1:
            interaction_col -= 1 if interaction_col - 1 >= 0 else 0
        elif self.direction[2] == 1:
            interaction_row -= 1 if interaction_row - 1 >= 0 else 0
        elif self.direction[3] == 1:
            interaction_row += 1 if interaction_row + 1 < self.n_rows else 0
        return interaction_row, interaction_col
