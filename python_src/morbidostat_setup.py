from morbidostat_experiment import morbidostat

def parse_meta(entries):
    return {entries[0]:entries[1]}

time_to_seconds = {"s":1, 'm':60, "h": 3600, "d": 60*60*24}
def parse_times(entries):
    k = entries[0]
    if len(entries)>2 and entries[2] in time_to_seconds:
        unit = time_to_seconds[entries[2]]
    else:
        unit = 1.0
    return {k:int(float(entries[1])*unit)}

def parse_parameters(entries):
    return {entries[0]:float(entries[1])}

def parse_drugs(entries):
    return [entries[0], entries[1]]

def parse_bottles(entries):
    return {entries[0]:map(float, entries[1:])}

def parse_vials(entries):
    return {int(entries[0])-1:{"feedback":entries[1], "bottles":entries[2:5], "feedback_drug": entries[5]}}

def parse_config_table(fname):
    parameters = {}
    drugs = []
    vials = {}
    bottles = {}
    with open(fname) as config:
        parse_cat = None
        for line in open(fname):
            entries = filter(lambda x:x!="", line.strip().split(','))
            if len(entries)==0:
                continue
            elif entries[0][0]=='#':
                parse_cat = entries[0][1:]
            elif entries[0]!="":
                if parse_cat=="meta":
                    parameters.update(parse_meta(entries))
                elif parse_cat=="times":
                    parameters.update(parse_times(entries))
                elif parse_cat=="parameters":
                    parameters.update(parse_parameters(entries))
                elif parse_cat=="drugs":
                    drugs.append(parse_drugs(entries))
                elif parse_cat=="bottles":
                    bottles.update(parse_bottles(entries))
                elif parse_cat=="vials":
                    vials.update(parse_vials(entries))

    return parameters, drugs, vials, bottles


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Instantiates a morbidostat')
    parser.add_argument('--config', required = True, type = str,  help ="CSV config file")
    parser.add_argument('--out', required = False, type = str,  help ="outpath")
    params = parser.parse_args()

    parameters, drugs, vials, bottles = parse_config_table(params.config)

    morb = morbidostat(vials = sorted(vials.keys()),
                       experiment_duration = parameters['experiment'],
                       cycle_dt = parameters['cycle'],
                       OD_dt = parameters['OD'],
                       dilution_factor = parameters['dilution'],
                       target_OD = parameters['target OD'],
                       bug = parameters['bug'],
                       experiment_name = parameters['name'],
                       drugs = [x[0] for x in drugs],
                       bottles = bottles.keys()
                       )

    morb.set_vial_properties(vials)
    morb.debug=False

    morb.drug_units = [x[1] for x in drugs]
    for bottle in morb.bottles:
        morb.set_drug_concentrations(bottle, bottles[bottle], initial=True)
