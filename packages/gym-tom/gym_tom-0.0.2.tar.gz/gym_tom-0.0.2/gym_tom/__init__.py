from gym.envs.registration import register

register(
    id="gym_tom/GridWorld-v0",
    entry_point="gym_tom.envs:GridWorldB",
)
