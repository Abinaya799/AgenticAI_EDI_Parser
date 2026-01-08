import json
from datetime import datetime

def extract_elements_with_rules(profile: dict, segments: dict, partner: str, edi_version: str):
    """
    Retrieve parsing rules from the profile and extract golden invoice data.
    """
    warnings = []
    confidence = 1.0
    our_broker = 'OURBROKER'
    pro = "null"
    load_id = "null"
    po = "null"
    ship_from = "null"
    ship_to = "null"    
    bill_to = "null"
    pickup = None
    delivery = None
    base_freight = 0.00
    fuel_surcharge = 0.00
    detention = 0.00
    other_l1 = []
    other_sac = []
    other = []
    l1_rules = None
    sac_rules = None
    ship_from_rule = {}
    ship_to_rule = {}
    bill_to_rule = {}
    pickup_date_rule = {}
    delivery_date_rule = {}


    header = profile['segments']['header']
    print(f"Header Segment: {header}")
    parties = profile['segments']['parties']
    print(f"Parties Segment: {parties}")
    dates = profile['segments']['dates']
    print(f"Dates Segment: {dates}")
    charges = profile['segments']['charges']
    print(f"Charges Segment: {charges}")
    total_rules = profile['segments']['total']
    print(f"Totals Segment: {total_rules}")
    currency_rules = profile['currency']
    print(f"Currency Segment: {currency_rules}")
    invoice_id_rule = header.get('invoice_id',{"seg":"inv_id_rule_in_profile"})
    print(f"Invoice ID rule: {invoice_id_rule}")
    invoice_date_rule = header.get('invoice_date',{"seg":"inv_date_rule_in_profile"})
    print(f"Invoice Date rule: {invoice_date_rule}")
    # bol_rule = header.get('bol',{"seg":"bol_rule_in_profile"}).get("firstOf")
    bol_rule = header.get('bol',[{"seg":"bol_rule_in_profile"}]).get("firstOf",[header.get('bol',[{"seg":"bol_rule_in_profile"}])])
    print(f"BOL rule: {bol_rule}")
    pro_rule = header.get('pro',{"seg":"pro_rule_in_profile"})
    print(f"PRO rule: {pro_rule}")
    header['load_id'] = {'seg': 'REF', 'qual': 'LO', 'idx': 2}
    load_id_rule = header.get('load_id',{"seg":"load_id_rule_in_profile"})
    print(f"Load ID rule: {load_id_rule}")
    for party in parties:
        if party['mapTo'] == "parties.ship_from":
            ship_from_rule = party
            print(f"Ship From rule: {ship_from_rule}")
        elif party['mapTo'] == "parties.ship_to":
            ship_to_rule = party
            print(f"Ship To rule: {ship_to_rule}")
        elif party['mapTo'] == "parties.bill_to":
            bill_to_rule = party
            print(f"Bill To rule: {bill_to_rule}")
    for date in dates:
        if date['mapTo'] == "dates.pickup":
            pickup_date_rule = date
            print(f"Ship Date rule: {pickup_date_rule}")
        elif date['mapTo'] == "dates.delivery":
            delivery_date_rule = date
            print(f"Delivery Date rule: {delivery_date_rule}")
    if charges['strategy'] == "L1_only" or charges['strategy'] == "L1_then_SAC":
        l1_rules = charges['l1_rules']
        sac_rules = None
        print(f"L1 Rules: {l1_rules}")
        if charges['strategy'] == "L1_then_SAC":
            sac_rules = charges['sac_rules']
            print(f"SAC Rules: {sac_rules}")
    elif charges['strategy'] == "SAC_only":
        l1_rules = None
        sac_rules = charges['sac_rules']
        print(f"SAC Rules: {sac_rules}")
    try:
        invoice_id = segments[invoice_id_rule['seg']][0][invoice_id_rule['idx']].strip()
        print(f"Invoice ID: {invoice_id}")
    except KeyError:
        invoice_id = None
        print("Invoice ID not found.")
        confidence = 0.1
        print(f"Confidence score dropped to 0.1: Invoice ID not found")
        raise ValueError("Invoice ID not found.")
        
    if our_broker == segments['GS'][0][3].strip():
        side = 'buy'
    else:
        side = 'sell'
    print(f"Side: {side}")
    source = { "type": "edi210", "doc_uri": "null"}
    print(f"Source: {source}")
    carrier = {"name": "null", "scac": "null"}
    print(f"Carrier: {carrier}")
    customer = {"name": "null", "account_id": "null"}
    print(f"Customer: {customer}")
    # bol = segments.get(bol_rule[0]['seg'], [])
    # if len(bol) > 0:
    #     bol = bol[0][bol_rule[0]['idx']].strip()
    # else:
    #     bol = segments.get(bol_rule[1]['seg'], [])
    #     if len(bol) > 0:
    #         for item in bol:
    #             bol = bol[0][bol_rule[1]['idx']].strip()
    #             if item[1].strip() == bol_rule[1]['qual']:
    #                 bol = bol[0][bol_rule[1]['idx']].strip()
    #     else:
    #         bol = "null"
    #         warnings.append(f"{bol_rule[1]['seg']} not found.")
    #         confidence -= 0.05
    #         print(f"Confidence score adjusted -0.05: {bol_rule[1]['seg']} not found.")
    # print(f"BOL: {bol}")
    no_bol_rule = False
    bol_seg = segments.get(bol_rule[0]['seg'], "null")
    print(f"1: {bol_seg}")
    if bol_seg == "null":
        try:
            bol_seg = segments.get(bol_rule[1]['seg'], "null")
            print(f"2: {bol_seg}")
        except:
            warnings.append(f"f{bol_rule[0]['seg']} not found")
            print(f"f{bol_rule[0]['seg']} not found")
            no_bol_rule = True
        if bol_seg == "null" and not no_bol_rule:
            bol = "null"
            warnings.append(f"bol not found")
            confidence -= 0.05
            print(f"Confidence score adjusted -0.05: bol not found.")
        elif bol_seg != "null":
            print(f"3: {bol_seg}")
            for each_ref in bol_seg:
                print(f"each_ref:{each_ref}")
                if each_ref[1] == bol_rule[1]['qual']:
                    bol = each_ref[bol_rule[1]['idx']]
                else:
                    bol = "null"
            if bol == "null":
                warnings.append(f"bol not found")
                confidence -= 0.05
                print(f"Confidence score adjusted -0.05: bol not found.")
    else:
        bol = bol_seg[0][bol_rule[0]['idx']]
    print(f"last bol: {bol}")

    # for rule in bol_rule:
    #     bol_seg = segments.get(rule['seg'],"null")
    #     if bol_seg != "null" and len(bol_seg) > rule['idx']:
    #         bol = bol_seg[rule['idx']]
    #     else:
    #         bol = "null"
    if segments.get(pro_rule['seg']) != "pro_rule_in_profile":
        if segments.get(pro_rule['seg']): 
            for pro_seg in segments[pro_rule['seg']]:
                if pro_seg[1].strip() == pro_rule.get('qual', 'CN'):
                    pro = pro_seg[pro_rule['idx']].strip()
                    print(f"PRO: {pro}")
        else:
            warnings.append(f"{pro_rule['seg']} not found.")
            confidence -= 0.05
            print(f"Confidence score adjusted -0.05: {pro_rule['seg']} not found.")
    else:
        warnings.append(f"{pro_rule['seg']} not found.")
    print(f"PRO: {pro}")
    print(f"PO: {po}")
    if segments.get(load_id_rule['seg']) != "load_id_rule_in_profile":
        if segments.get(load_id_rule['seg']):
            for load_id_seg in segments[load_id_rule['seg']]:
                if load_id_seg[1].strip() == load_id_rule.get('qual', 'LO'):
                    load_id = load_id_seg[pro_rule['idx']].strip()
        else:
            warnings.append(f"{load_id_rule['seg']} not found.")
            confidence -= 0.05
            print(f"Confidence score adjusted -0.05: {load_id_rule['seg']} not found.")
    else:
        warnings.append(f"{load_id_rule['seg']} not found.")
    print(f"Load ID: {load_id}")
    if len(parties) == 0:
        warnings.append("No parties rules defined in profile.")
    else:
        if segments.get(parties[0]['seg']) is None:
            warnings.append(f"{parties[0]['seg']} segment not found.")
            confidence -= 0.05
            print(f"Confidence score adjusted -0.05: {parties[0]['seg']} not found.")
        else:
            for N1_seg in segments[parties[0]['seg']]:
                if N1_seg[1] == ship_from_rule.get('qual'):
                    ship_from = N1_seg[ship_from_rule['nameIdx']].strip()
                elif N1_seg[1] == ship_to_rule.get('qual'):
                    ship_to = N1_seg[ship_to_rule['nameIdx']].strip()
                elif N1_seg[1] == bill_to_rule.get('qual'):
                    bill_to = N1_seg[bill_to_rule['nameIdx']].strip()
    print(f"Ship From: {ship_from}")
    print(f"Ship To: {ship_to}")
    print(f"Bill To: {bill_to}")
    if len(dates) == 0:
        warnings.append("No dates rules defined in profile.")
    else:
        if segments.get(dates[0]['seg']) is None:
            warnings.append(f"{dates[0]['seg']} segment not found.")
            confidence -= 0.05
            print(f"Confidence score adjusted -0.05: {dates[0]['seg']} not found.")
        else:
            for date in segments[dates[0]['seg']]:
                if date[1] == pickup_date_rule.get('qual',"11"):
                    pickup_str = date[2].strip()
                    pickup = datetime.strptime(pickup_str, "%Y%m%d").strftime("%Y-%m-%d")
                elif date[1] == delivery_date_rule.get('qual',"70"):
                    delivery_str = date[2].strip()
                    delivery = datetime.strptime(delivery_str, "%Y%m%d").strftime("%Y-%m-%d")

    print(f"Pickup Date: {pickup}")
    print(f"Delivery Date: {delivery}") 
    try:
        invoice_date_str = segments[invoice_date_rule['seg']][0][invoice_date_rule['idx']].strip()
        invoice_date = datetime.strptime(invoice_date_str, "%Y%m%d").strftime("%Y-%m-%d")
        print(f"Invoice Date: {invoice_date}")
    except KeyError:
        invoice_date = "null"
        warnings.append(f"{invoice_date_rule['seg']} not found.")
        confidence = 0.1
        print(f"Confidence score dropped to 0.1: Invoice date not found")
    if l1_rules:
        existing_codes = []
        compute_l1 = True
        # print(l1_rules)
        # print(segments['L1'])
        if charges['strategy'] == "L1_only": 
            try:
                segments['L1']
            except KeyError:
                raise KeyError("L1 segment not found.")
        elif charges['strategy'] == "L1_then_SAC":
            compute_l1 = segments.get('L1', False)
        if compute_l1:
            for l1_rule in l1_rules:
                print(f"L1 Rule: {l1_rule}")
                mapto = l1_rule.get('mapTo','charges.defaultother').split('.')[-1]
                print(f"MapTo: {mapto}")
                contains = l1_rule.get('contains', [])
                print(f"Contains: {contains}")
                for l1_charge in segments['L1']:
                    print(f"L1 Charge: {l1_charge}")
                    if any(c in l1_charge for c in contains):
                        if mapto == "base_freight":
                            base_freight += float(l1_charge[2].strip())
                            existing_codes.append(l1_charge[5].strip())
                            for i, d in enumerate(other_l1):
                                if d['code'] == l1_charge[5].strip():
                                    other_l1.pop(i)                              
                            print(f"Base Freight updated: {base_freight}")
                        elif mapto == "fuel_surcharge":
                            fuel_surcharge += float(l1_charge[2].strip())
                            existing_codes.append(l1_charge[5].strip())
                            for i, d in enumerate(other_l1):
                                if d['code'] == l1_charge[5].strip():
                                    other_l1.pop(i)
                            print(f"Fuel Surcharge updated: {fuel_surcharge}")
                        elif mapto == "detention":
                            detention += float(l1_charge[2].strip())
                            existing_codes.append(l1_charge[5].strip())
                            for i, d in enumerate(other_l1):
                                if d['code'] == l1_charge[5].strip():
                                    other_l1.pop(i)
                            print(f"Detention updated: {detention}")
                    else:
                        if mapto == "defaultother":
                            pass
                        if l1_charge[5].strip() not in existing_codes:
                            other_l1.append({
                                "code": l1_charge[5].strip(),
                                "desc": l1_charge[-1].strip(),
                                "amount": float(l1_charge[2].strip())
                            })
                            existing_codes.append(l1_charge[5].strip())
                            # warnings.append(f"Other charge added: {l1_charge[-1].strip()} - {l1_charge[2].strip()}")
                            # confidence -= 0.1
            for other_charge in other_l1:
                warnings.append(f"Other charge added: {other_charge['code']} = {other_charge['amount']}")
                confidence -= 0.1
                print(f"confidence score adjusted -0.1: Other charge added: {other_charge['code']} = {other_charge['amount']}")
        else:
            warnings.append("L1 segment not found.")
            confidence -= 0.1
            print("Confidence score adjusted -0.1: L1 segment not found.")
    if sac_rules:
        existing_codes = []
        compute_sac = True
        if charges['strategy'] == "SAC_only": 
            try:
                segments['SAC']
            except KeyError:
                raise KeyError("SAC segment not found.")
        elif charges['strategy'] == "L1_then_SAC":
            compute_sac = segments.get('SAC', False)
        if compute_sac:
            for sac_rule in sac_rules:
                print(f"SAC_Rule: {sac_rule}")
                mapto = sac_rule.get('mapTo','charges.defaultother').split('.')[-1]
                print(f"MapTo: {mapto}")
                codeIn = sac_rule.get('codeIn', [])
                print(f"codeIn: {codeIn}")
                for sac_charge in segments['SAC']:
                    # print(f"SAC Charge: {SAc_charge}")
                    if any(c in sac_charge for c in codeIn):
                        if mapto == "fuel_surcharge":
                            fuel_surcharge += float(sac_charge[5].strip())
                            existing_codes.append(sac_charge[2].strip())
                            print(f"fuel_sur_code added: {existing_codes}")
                            for i, d in enumerate(other_sac):
                                if d['code'] == sac_charge[2].strip():
                                    other_sac.pop(i)
                            # print(f"Base Freight updated: {base_freight}")
                        elif mapto == "detention":
                            detention += float(sac_charge[5].strip())
                            existing_codes.append(sac_charge[2].strip())
                            print(f"detention_code added: {existing_codes}")
                            for i, d in enumerate(other_sac):
                                if d['code'] == sac_charge[2].strip():
                                    other_sac.pop(i)
                            # print(f"Fuel Surcharge updated: {fuel_surcharge}")
                    else:
                        if mapto == "defaultother":
                            pass
                        if sac_charge[2].strip() not in existing_codes:
                            other_sac.append({
                                "code": sac_charge[2].strip(),
                                "desc": sac_charge[-1].strip(),
                                "amount": float(sac_charge[5].strip())
                            })
                            existing_codes.append(sac_charge[2].strip())
                            # print(f"sac_other_code added: {existing_codes}")
                            # warnings.append(f"Other charge added: {sac_charge[-1].strip()} - {sac_charge[2].strip()}")
                            # confidence -= 0.1
            for other_charge in other_sac:
                warnings.append(f"Other charge added: {other_charge['code']} = {other_charge['amount']}")
                confidence -= 0.1
                print(f"confidence score adjusted -0.1: Other charge added: {other_charge['code']} = {other_charge['amount']}")
        else:
            warnings.append("SAC segment not found.")
            confidence -= 0.1
            print(f"confidence score adjusted -0.1: SAC segment not found.")
    other = other_l1+other_sac
    print(f"Base Freight: {base_freight}")
    print(f"Fuel Surcharge: {fuel_surcharge}")
    print(f"Detention: {detention}")
    print(f"Other Charges: {other}")
    sum_total = 0.00
    sum_total += base_freight
    sum_total += fuel_surcharge
    sum_total += detention
    for oth in other:
        print(f"Adding Other Charge: {oth['desc']} - {oth['amount']}")
        sum_total += oth['amount']
    sum_total = round(sum_total, 2)
    print(f"Sum Total from Charges: {sum_total}")

    if segments.get(total_rules['seg']): 
        total = segments[total_rules['seg']][0][total_rules['idx']].strip()
        print(f"Total from EDI: {total}")
    else:
        total = sum_total
        warnings.append("Total segment not found.")
        confidence -= 0.15
        print("confidence score adjusted -0.15: Total segment not found.")

    if sum_total != float(total):
        warnings.append(f"Total from EDI {total} does not match sum of charges {sum_total}.")
        confidence -= 0.1
        print("confidence score adjusted -0.1: Total from EDI {total} does not match sum of charges {sum_total}.")
    currency = currency_rules['default']
    print(f"Currency: {currency}")
    golden_invoice = {
        "invoice_id": invoice_id,
        "side": side,
        "source": { "type": "edi210", "doc_uri": 'null' },
        "carrier": { "name": 'null', "scac": 'null' },
        "customer": { "name": 'null', "account_id": 'null' },
        "refs": { "bol": bol, "pro": pro, "po": 'null', "load_id": load_id },
        "parties": { "ship_from": ship_from, "ship_to": ship_to, "bill_to": bill_to },
        "dates": { "invoice": invoice_date, "pickup": pickup, "delivery": delivery },
        "currency": currency,
        "charges": {
        "base_freight": base_freight,
        "fuel_surcharge": fuel_surcharge,
        "detention": detention,
        "other": other
        },
        "total": total,
        "metadata": {
        "golden_schema_version": "0.1",
        "parser_version": "1.0.0",
        "edi_version": edi_version,
        "trading_partner": partner,
        "confidence": confidence
        },
        "evidence": { "doc_uri": 'null', "attachments": [] }
    }
    print(json.dumps(golden_invoice, indent=2))
    print("Warnings:")
    for warn in warnings:
        print(f"- {warn}")
    return golden_invoice, warnings



        
    
    
