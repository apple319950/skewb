import gym
import rubiks_cube_gym

# 先手動 import skewb 模組
import rubiks_cube_gym.envs.skewb
import rubiks_cube_gym.envs.skewb_sarah

print("registered gym envs containing skewb:")

for env_id in gym.envs.registry.keys():
    if "skewb" in env_id.lower():
        print(env_id)