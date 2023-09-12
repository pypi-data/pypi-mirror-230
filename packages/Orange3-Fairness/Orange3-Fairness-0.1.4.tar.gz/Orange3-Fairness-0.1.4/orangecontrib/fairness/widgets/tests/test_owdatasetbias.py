import unittest

from Orange.data.table import Table
from Orange.widgets.tests.base import WidgetTest
from Orange.widgets.tests.utils import simulate
from Orange.widgets.utils.itemmodels import select_rows

from orangecontrib.fairness.widgets.owasfairness import OWAsFairness
from orangecontrib.fairness.widgets.owdatasetbias import OWDatasetBias
from orangecontrib.fairness.widgets.tests.utils import as_fairness_setup


class TestOWDatasetBias(WidgetTest):
    def setUp(self) -> None:
        self.test_data_path = "https://datasets.biolab.si/core/adult.tab"
        self.test_incorrect_input_data_path = "https://datasets.biolab.si/core/breast-cancer.tab"
        self.widget = self.create_widget(OWDatasetBias)
        self.as_fairness = self.create_widget(OWAsFairness)

        self.assertEqual(self.widget.disparate_impact_label.text(), "No data detected.")
        self.assertEqual(self.widget.statistical_parity_difference_label.text(), "")

    def test_no_data(self):
        """Check that the widget doesn't crash on empty data"""
        self.send_signal(self.widget.Inputs.data, None)
        self.assertEqual(self.widget.disparate_impact_label.text(), "No data detected.")
        self.assertEqual(self.widget.statistical_parity_difference_label.text(), "")

    def test_incorrect_input_data(self):
        """Check that the widget displays an error message when the input data does not have the 'AsFairness' attributes"""
        test_data = Table(self.test_incorrect_input_data_path)
        self.send_signal(self.widget.Inputs.data, test_data)
        self.assertTrue(self.widget.Error.missing_fairness_data.is_shown())

    def test_input_as_fairness_data(self):
        """Check that the widget works with data from the as fairness widget"""
        test_data = as_fairness_setup(self)
        self.send_signal(
            self.as_fairness.Inputs.data,
            test_data,
        )
        simulate.combobox_activate_item(
            self.as_fairness.controls.favorable_class_value, ">50K"
        )
        simulate.combobox_activate_item(
            self.as_fairness.controls.protected_attribute, "sex"
        )
        select_rows(self.as_fairness.controls.privileged_pa_values, [1])
        output_data = self.get_output(self.as_fairness.Outputs.data)

        self.send_signal(self.widget.Inputs.data, output_data)
        self.assertTrue(
            self.widget.disparate_impact_label.text().startswith(
                "Disparate Impact (ideal = 1):"
            )
        )
        self.assertTrue(
            self.widget.statistical_parity_difference_label.text().startswith(
                "Statistical Parity Difference (ideal = 0):"
            )
        )


if __name__ == "__main__":
    unittest.main()
