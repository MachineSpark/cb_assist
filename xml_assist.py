import pytest
import xml.etree.ElementTree as ET


packetEDP_xml_path = r"""X:\Downloads\headHunterTest-main\PacketEPD.xml"""
ED807_xml_path = r"""X:\Downloads\headHunterTest-main\20220713_ED807_full.xml"""

ED807_root = ET.parse(ED807_xml_path).getroot()
packetEDP_root = ET.parse(packetEDP_xml_path).getroot()

all_ED101 = packetEDP_root.findall('ED101')
namespace = {"xmlns": "urn:cbr-ru:ed:v2.0"}
all_BICDirectoryEntry = ED807_root.findall('xmlns:BICDirectoryEntry', namespaces=namespace)



def test_EDQuantity():
    # Проверяет что EDQuantity в root PacketEPD.xml совпадает с количеством сформированных ED101
    # Требование 2.2.1, тест кейс tc4.3
    root_EDQuantity = int(packetEDP_root.attrib['EDQuantity'])
    expected_EDQuantity = len(all_ED101)
    print(f"root EDQuantity: {root_EDQuantity}. Рассчитанное EDQuantity: {expected_EDQuantity}")
    assert root_EDQuantity == expected_EDQuantity


def test_Sum():
    # Проверяет что Sum в root PacketEPD.xml соответствует сумме всех Sum включенных из ED101 того же файла
    # Требование 2.2.1, тест кейс tc4.4
    root_sum = int(packetEDP_root.attrib['Sum'])
    expected_sum = 0
    for i, ed101 in enumerate(all_ED101):
        expected_sum += int(ed101.get('Sum'))
        # print(i, ed101.get('Sum'))
    print(f"Root Sum: {root_sum}. Рассчитанная ожидаемая Sum: {expected_sum}")
    assert root_sum == expected_sum


def test_EDAuthor():
    # Проверяет соответствие значение EDAuthor заголовку пакета PacketEPD.xml
    # Требование 2.2.2, тест кейс tc4.7
    root_author = packetEDP_root.attrib['EDAuthor']
    for ed101 in all_ED101:
        assert root_author == ed101.get('EDAuthor')


def test_EDDate():
    # Проверяет соответствие значение EDDate заголовку пакета
    # Требование 2.2.2, тест кейс tc4.6
    root_date = packetEDP_root.attrib['EDDate']
    for ed101 in all_ED101:
        assert root_date == ed101.get('EDDate')


def test_EdNo():
    # Проверяет корректную инкрементацию порядково номера EdNo в каждом следующем ED101
    # Требование 2.2.2, тест кейс tc4.8
    expected_EdNo = 1
    for ed101 in all_ED101:
        assert expected_EdNo == int(ed101.get('EDNo'))
        expected_EdNo += 1


def test_payer_AccDocNo():
    # Проверяет корректное заполнения данных AccDocNo в PacketEPD.xml
    # Требование 2.2.2.1, тест кейс tc4.9
    all_ed101_AccDocNo = []
    for accdoc in packetEDP_root.findall('ED101/AccDoc'):
        all_ed101_AccDocNo.append(accdoc.get('AccDocNo'))
    all_pt_type = []
    for entry in all_BICDirectoryEntry[::2]:
        pt_type = entry.find('xmlns:ParticipantInfo', namespaces=namespace).get('PtType')
        all_pt_type.append(pt_type)
    for i, accdocno in enumerate(all_ed101_AccDocNo):
        assert all_pt_type[i] == accdocno, f"AccDocNo не соответствует ожидаемому. Порядковый номер ED101 {i+1}"


def test_payer_AccDocDate():
    # Проверяет корректное заполнения данных DateIn в PacketEPD.xml
    # Требование 2.2.2.1, тест кейс tc4.10
    all_ed101_AccDocDate = []
    for accdoc in packetEDP_root.findall('ED101/AccDoc'):
        all_ed101_AccDocDate.append(accdoc.get('AccDocDate'))
    all_date_in = []
    for entry in all_BICDirectoryEntry[::2]:
        date_in = entry.find('xmlns:ParticipantInfo', namespaces=namespace).get('DateIn')
        all_date_in.append(date_in)
    for i, accdocdate in enumerate(all_ed101_AccDocDate):
        assert all_date_in[i] == accdocdate, f"AccDocDate не соответствует ожидаемому. Порядковый номер ED101 {i+1}"


def test_payer_Sum():
    # Проверяет корректное заполнения данных Sum в PacketEPD.xml
    # Требование 2.2.2.1, тест кейс tc4.11
    all_ed101_Sum = []
    for ed101 in packetEDP_root.findall('ED101'):
        all_ed101_Sum.append(ed101.get('Sum'))
    all_rgn = []
    for entry in all_BICDirectoryEntry[::2]:
        rgn = entry.find('xmlns:ParticipantInfo', namespaces=namespace).get('Rgn')
        all_rgn.append(rgn)
    for i, ed101_sum in enumerate(all_ed101_Sum):
        assert all_rgn[i] == ed101_sum, f"Sum не соответствует ожидаемому. Порядковый номер ED101 {i+1}"


def test_payer_Name():
    # Проверяет корректное заполнения данных Name плательщика в PacketEPD.xml
    # Требование 2.2.2.1, тест кейс tc4.12
    all_ed101_payer_name = []
    for name in packetEDP_root.findall('ED101/Payer/Name'):
        all_ed101_payer_name.append(name.text)
    all_namep = []
    for entry in all_BICDirectoryEntry[::2]:
        namep = entry.find('xmlns:ParticipantInfo', namespaces=namespace).get('NameP')
        all_namep.append(namep)
    for i, name in enumerate(all_ed101_payer_name):
        assert all_namep[i] == name, f"Имя плательщика не соответствует ожидаемому. Порядковый номер ED101 {i+1}"


def test_payer_BIC():
    # Проверяет корректное заполнения данных BIC в PacketEPD.xml
    # Требование 2.2.2.1, тест кейс tc4.13
    all_ed101_payer_bic = []
    for bank in packetEDP_root.findall('ED101/Payer/Bank'):
        all_ed101_payer_bic.append(bank.get('BIC'))
    all_ed807_bic = []
    for entry in all_BICDirectoryEntry[::2]:
        all_ed807_bic.append(entry.get('BIC'))
    for i, ed101_bic in enumerate(all_ed101_payer_bic):
        assert all_ed807_bic[i] == ed101_bic, \
            f"BIC плательщика не соответствует ожидаемому. Порядковый номер ED101 {i+1}"


def test_payee_Name():
    # Проверяет корректное заполнения данных Name получателя в PacketEPD.xml
    # Требование 2.2.2.2, тест кейс tc4.14
    all_ed101_payee_name = []
    for name in packetEDP_root.findall('ED101/Payee/Name'):
        all_ed101_payee_name.append(name.text)
    all_namep = []
    for entry in all_BICDirectoryEntry[1::2]:
        namep = entry.find('xmlns:ParticipantInfo', namespaces=namespace).get('NameP')
        all_namep.append(namep)
    for i, name in enumerate(all_ed101_payee_name):
        assert all_namep[i] == name, f"Имя получателя не соответствует ожидаемому. Порядковый номер ED101 {i+1}"


def test_payee_BIC():
    # Проверяет корректное заполнения данных BIC получателя в PacketEPD.xml
    # Требование 2.2.2.1, тест кейс tc4.15
    all_ed101_payee_bic = []
    for bank in packetEDP_root.findall('ED101/Payee/Bank'):
        all_ed101_payee_bic.append(bank.get('BIC'))
    all_ed807_bic = []
    for entry in all_BICDirectoryEntry[1::2]:
        all_ed807_bic.append(entry.get('BIC'))
    for i, ed101_bic in enumerate(all_ed101_payee_bic):
        assert all_ed807_bic[i] == ed101_bic, \
            f"BIC получателя не соответствует ожидаемому. Порядковый номер ED101 {i+1}"
