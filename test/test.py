from DroneBlocksTelloSimulator.DroneBlocksSimulatorContextManager import DroneBlocksSimulatorContextManager

# https://coding-sim.droneblocks.io/

if __name__ == '__main__':

    sim_key = '1d6c14be-3cb1-4d90-8077-f2cb1699cba5'
    distance = 40
    with DroneBlocksSimulatorContextManager(simulator_key=sim_key) as drone:
        # print(drone.get_battery())
        drone.stream_on()
        drone.takeoff()
        # drone.fly_forward(distance, 'in')
        # drone.fly_left(distance, 'in')
        # drone.fly_backward(distance, 'in')
        # drone.fly_right(distance, 'in')
        # drone.flip_backward()
        drone.land()
