import pytest
from decimal import Decimal
from mb_test_task.base import Circle, Triangle


class TestCircle:
    """Test circle class
    """

    @pytest.mark.parametrize('radius', [-3.1, 0.0])
    def test_radicus_cant_be_onpositive(self, radius: float) -> None:
        """Test circle radius cant be nonpositive
        """
        with pytest.raises(
            ValueError,
            match='Radius must be a positive float'
                ):
            Circle({'radius': radius})

    @pytest.mark.parametrize('radius,area', [(3.0, 28.2743), ])
    def test_area_calculation(self, radius: float, area: float) -> None:
        """Test area result
        """
        c = Circle({'radius': radius})
        assert float(round(Decimal(c.area()), 4)) == area, 'wrong area'


class TestTriangle:
    """Test triangle class
    """

    @pytest.mark.parametrize('a,b,c', [
        (-3.1, 0.0, -7.0),
        (3.1, 0.0, 7.0),
        (-3.1, -1.1, -7.0),
        (0.0, 1.1, -7.0),
        (3.1, 1.1, -7.0),
            ])
    def test_radicus_cant_be_onpositive(
        self,
        a: float,
        b: float,
        c: float,
            ) -> None:
        """Test triangle sizes cant be nonpositive
        """
        with pytest.raises(
            ValueError,
            match='All sides of triangle must have a positive float value'
                ):
            Triangle({'a': a, 'b': b, 'c': c})

    def test_wrong_shape_of_triangle(self) -> None:
        """Test wrong shape of triangle raises error
        """
        with pytest.raises(
            ValueError,
            match='Triangle must have 3 sides'
                ):
            Triangle({'a': 1, 'b': 2})
        with pytest.raises(
            ValueError,
            match='Triangle must have 3 sides'
                ):
            Triangle({'a': 1, 'b': 2, 'aa': 1, 'bb': 2})

    @pytest.mark.parametrize('a,b,c,area', [
        (1.0, 1.0, 1.0, 0.433013),
        ])
    def test_area_calculation(
        self,
        a: float,
        b: float,
        c: float,
        area: float
            ) -> None:
        """Test area result
        """
        c = Triangle({'a': a, 'b': b, 'c': c})
        assert float(round(Decimal(c.area()), 6)) == area, 'wrong area'

    @pytest.mark.parametrize('a,b,c,right', [
        (3.0, 4.0, 5.0, True),
        (5.0, 5.0, 6.0, False),
            ])
    def test_is_right(
        self,
        a: float,
        b: float,
        c: float,
        right: bool
            ) -> None:
        """Test is right triangle
        """
        c = Triangle({'a': a, 'b': b, 'c': c})
        assert c.is_right() == right, 'wrong check result'
