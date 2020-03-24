import gym
import numpy as np
import os
import tensorflow as tf
import time
import random

from stable_baselines import DQN
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.a2c.utils import conv, conv_to_fc, linear

from callback import CustomCallback

def evaluate(model, num_episodes=100):
    """
    Evaluate a RL agent
    :param model: (BaseRLModel object) the RL Agent
    :param num_episodes: (int) number of episodes to evaluate it
    :return: (float) Mean reward for the last num_episodes
    """
    env = model.get_env()
    all_episode_rewards = []
    hist = np.zeros(15, dtype=int)
    for _ in range(num_episodes):
        done = False
        obs = env.reset()
        env.render()
        while not done:
            action, _states = model.predict(obs)
            obs, reward, done, extras = env.step(action)
            if reward < 0:
                action = random.sample(range(4),1)[0]
                obs, reward, done, extras = env.step(action)
            # time.sleep(.1)
            env.render()
        hist[env.maximum_tile()] += 1
        all_episode_rewards.append(extras['score'])

    mean_episode_reward = np.mean(all_episode_rewards)
    print("Reward: ", mean_episode_reward)
    print('Histogram of maximum tile achieved:')
    for i in range(1,15):
        if hist[i] > 0:
            print(f'{2**i}: {hist[i]}')

def my_cnn(image, **kwargs):
    """
    :param in: (TensorFlow Tensor) Image input placeholder
    :param kwargs: (dict) Extra keywords parameters for the convolutional layers of the CNN
    :return: (TensorFlow Tensor) The CNN output layer
    """
    activ = tf.nn.relu
    print("image", image)
    layer_1 = activ(conv(image, 'c1', n_filters=222, filter_size=2, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_2 = activ(conv(layer_1, 'c2', n_filters=222, filter_size=2, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_3 = activ(conv(layer_2, 'c3', n_filters=222, filter_size=2, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_4 = activ(conv(layer_3, 'c4', n_filters=222, filter_size=2, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_5 = activ(conv(layer_4, 'c5', n_filters=222, filter_size=2, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_lin = conv_to_fc(layer_5)
    return layer_lin


if __name__ == '__main__':

    env_id = "gym_text2048:Text2048-v0"
    env = gym.make(env_id, cnn=True)
    model_name = 'models/cnn_5l_dueling_prioritized_lr'

    if False and os.path.exists(f'{model_name}.zip'):
        dqn_model = DQN.load(model_name)
        dqn_model.set_env(env)
    else:
        dqn_model = DQN('CnnPolicy', env, verbose=1, exploration_final_eps=.1, double_q=False, policy_kwargs={'cnn_extractor': my_cnn})

    callback = CustomCallback(verbose=1)
    dqn_model.learn(total_timesteps=10000, log_interval=10, callback=callback)
    dqn_model.save(f'{model_name}_3M')
    # mean_reward = evaluate(dqn_model, num_episodes=10)
