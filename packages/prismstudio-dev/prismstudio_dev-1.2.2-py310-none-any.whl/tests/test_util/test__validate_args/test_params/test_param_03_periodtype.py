import pytest

from prism._common.const import PeriodType
from prism._utils.validate_utils import _validate_args
from prism._utils.exceptions import PrismTypeError, PrismValueError


@_validate_args
def consensus(
    dataitemid: int,
    periodtype: str,
    periodout: int = 0,
    currency: str = 'trade',
) -> PeriodType:
    """
    valid periodtype =
        'Annual', 'A', 'Semi-Annual', 'SA', 'Quarterly', 'Q', 'YTD', 'LTM', 'Non-Periodic', 'NTM', 'Q-SA'
    """
    return periodtype


def test_periodtype_param():
    assert consensus(0, 'Annual', 0, 'trade') == PeriodType.ANNUAL

    # check type
    assert isinstance(consensus(0, 'Annual', 0, 'trade'), PeriodType)

    # valid periodtype param
    assert consensus(1, 'Annual') == PeriodType.ANNUAL
    assert consensus(2, 'A') == PeriodType.A
    assert consensus(3, 'Semi-Annual') == PeriodType.SEMI_ANNUAL
    assert consensus(4, 'SA') == PeriodType.SA
    assert consensus(5, 'Quarterly') == PeriodType.QUARTERLY
    assert consensus(6, 'Q') == PeriodType.Q
    assert consensus(7, 'YTD') == PeriodType.YTD
    assert consensus(8, 'LTM') == PeriodType.LTM
    assert consensus(9, 'Non-Periodic') == PeriodType.NON_PERIODIC
    assert consensus(10, 'NTM') == PeriodType.NTM
    assert consensus(11, 'Q-SA') == PeriodType.QSA

    assert consensus(1, periodtype='Annual') == PeriodType.ANNUAL
    assert consensus(2, periodtype='A') == PeriodType.A
    assert consensus(3, periodtype='Semi-Annual') == PeriodType.SEMI_ANNUAL
    assert consensus(4, periodtype='SA') == PeriodType.SA
    assert consensus(5, periodtype='Quarterly') == PeriodType.QUARTERLY
    assert consensus(6, periodtype='Q') == PeriodType.Q
    assert consensus(7, periodtype='YTD') == PeriodType.YTD
    assert consensus(8, periodtype='LTM') == PeriodType.LTM
    assert consensus(9, periodtype='Non-Periodic') == PeriodType.NON_PERIODIC
    assert consensus(10, periodtype='NTM') == PeriodType.NTM
    assert consensus(11, periodtype='Q-SA') == PeriodType.QSA


def test_wrong_periodtype_param():
    # wrong value
    with pytest.raises(PrismValueError):
        assert consensus(1, 'annual') == PeriodType.ANNUAL

    with pytest.raises(PrismValueError):
        assert consensus(1, 'a') == PeriodType.A

    with pytest.raises(PrismValueError):
        assert consensus(1, 'typo period')

    with pytest.raises(PrismValueError):
        assert consensus(1, 'q-SA') == PeriodType.QSA

    # wrong type
    with pytest.raises(PrismTypeError):
        assert consensus(1, periodtype=0, currency='won')

    with pytest.raises(PrismTypeError):
        assert consensus(2, 0)

    with pytest.raises(PrismTypeError):
        assert consensus(3, 'Annual', '0') == PeriodType.ANNUAL
