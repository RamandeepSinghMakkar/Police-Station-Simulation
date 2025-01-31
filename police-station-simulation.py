import simpy.rt
import random
import datetime

CRIME_PRIORITIES = {
    'murder': 1,
    'stalking': 2,
    'theft': 3,
    'bike stealing': 4,
    'pickpocket': 5
}

class PoliceStation:
    def __init__(self, env, num_officers, num_desks):
        self.env = env
        self.officers = [f"officer {i+1}" for i in range(num_officers)]
        self.mla = [simpy.PreemptiveResource(env, 1) for _ in range(num_officers)]
        self.desks = simpy.PriorityResource(env, num_desks)
        self.crime_count = {crime: 0 for crime in CRIME_PRIORITIES}
        self.criminals_caught = 0
        self.criminals_not_caught = 0
        self.criminals_caught_by_officer = {officer: 0 for officer in self.officers}

    def handle_case(self, citizen, crime_type, priority):
        arrival_time = datetime.timedelta(seconds=self.env.now)
        self.crime_count[crime_type] += 1
        print(f'Citizen {citizen} arrived at the police station at {arrival_time} for {crime_type} with priority {priority}.')
        arrivetime = self.env.now

        for i in range(len(self.officers)):
            if self.mla[i].count == 0:
                officer = self.officers[i]
                break

        with self.mla[i].request(priority=priority) as req, self.desks.request(priority=priority) as desk:
            yield req & desk
            assign_time = datetime.timedelta(seconds=self.env.now)
            print(f'Citizen {citizen} assigned to {officer} at {assign_time} for {crime_type} with priority {priority}.')
            assigntime = self.env.now
            try:
                yield self.env.timeout(random.randint(150, 300))
                if random.randint(0, 1) == 1:
                    self.criminals_caught += 1
                    self.criminals_caught_by_officer[officer] += 1
                    regsiter_time = datetime.timedelta(seconds=self.env.now)
                    print(f'Citizen {citizen} case for {crime_type} registered at {regsiter_time}. Criminal caught by {officer}.')
                else:
                    self.criminals_not_caught += 1
                    regsiter_time = datetime.timedelta(seconds=self.env.now)
                    print(f'Citizen {citizen} case for {crime_type} registered at {regsiter_time}. Criminal not caught.')
            except simpy.Interrupt:
                interrupt_time = datetime.timedelta(seconds=self.env.now)
                print(f'Citizen {citizen} case for {crime_type} was interrupted at {interrupt_time}.')

    def high_priority_case(self):
        wait_time = max(0, 600 - self.env.now)  # Calculate the wait time
        yield self.env.timeout(wait_time)
        for officer in self.officers:
            if self.mla[self.officers.index(officer)].count == 0:
                print(f'High-priority case (MLA) handled by {officer} at {datetime.timedelta(seconds=self.env.now)}.')
                yield self.env.timeout(random.randint(600, 900))
                break


    def run(self):
        num_citizens = random.randint(100, 150)
        interarrival_time = random.randint(300, 600)


        for i in range(num_citizens):
            crime_type = random.choice(list(CRIME_PRIORITIES.keys()))
            priority = CRIME_PRIORITIES[crime_type]

            # If Citizen 6 is the MLA, handle their case as high-priority
            if i == 1:
                self.env.process(self.high_priority_case())
            else:
                self.env.process(self.handle_case(i + 1, crime_type, priority))

            yield self.env.timeout(random.randint(150, 210))


    def shift_change(self):
        while True:
            yield self.env.timeout(15 * 60)  #shift change in 15 minutes
            shift_change_time = datetime.timedelta(seconds=self.env.now)
            print(f'--- Shift change at {shift_change_time} ---')

def run_simulation(num_officers, num_desks):
    env = simpy.rt.RealtimeEnvironment(factor=0.1)
    police_station = PoliceStation(env, num_officers, num_desks)

    env.process(police_station.run())
    env.process(police_station.shift_change())
    env.run(until=30 * 60)

    print(f"Number of cases registered: {sum(police_station.crime_count.values())}")
    print(f"Number of criminals caught: {police_station.criminals_caught}")
    print(f"Number of criminals not caught: {police_station.criminals_not_caught}")
    print("Criminals caught by each officer:")
    for officer, count in police_station.criminals_caught_by_officer.items():
        print(f"{officer}: {count}")

if __name__ == "__main__":
    num_officers = 5
    num_desks = 3

    run_simulation(num_officers, num_desks)
