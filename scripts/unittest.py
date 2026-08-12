import unittest
from unittest.mock import MagicMock

class TestModelFit(unittest.TestCase):
    
    def setUp(self):
        self.model = MagicMock()
        self.X_train = [[1, 2], [3, 4]]
        self.y_train = [0, 1]
        self.X_test = [[5, 6]]
        self.y_test = [1]
        self.EPOCHS = 10
        self.BATCH_SIZE = 2
        self.earlyStoppingCallback = MagicMock()
    
    def test_happy_path(self):
        history = self.model.fit(
            x=self.X_train,
            y=self.y_train,
            validation_data=(self.X_test, self.y_test),
            epochs=self.EPOCHS,
            batch_size=self.BATCH_SIZE,
            callbacks=[self.earlyStoppingCallback]
        )
        self.model.fit.assert_called_once()
    
    def test_empty_training_data(self):
        with self.assertRaises(ValueError):
            history = self.model.fit(
                x=[],
                y=[],
                validation_data=(self.X_test, self.y_test),
                epochs=self.EPOCHS,
                batch_size=self.BATCH_SIZE,
                callbacks=[self.earlyStoppingCallback]
            )
    
    def test_mismatched_shapes(self):
        with self.assertRaises(ValueError):
            history = self.model.fit(
                x=self.X_train,
                y=[[0], [1]],
                validation_data=(self.X_test, self.y_test),
                epochs=self.EPOCHS,
                batch_size=self.BATCH_SIZE,
                callbacks=[self.earlyStoppingCallback]
            )
    
    def test_large_batch_size(self):
        with self.assertRaises(ValueError):
            history = self.model.fit(
                x=self.X_train,
                y=self.y_train,
                validation_data=(self.X_test, self.y_test),
                epochs=self.EPOCHS,
                batch_size=len(self.X_train) + 1,
                callbacks=[self.earlyStoppingCallback]
            )
    
    def test_non_integer_epochs(self):
        with self.assertRaises(TypeError):
            history = self.model.fit(
                x=self.X_train,
                y=self.y_train,
                validation_data=(self.X_test, self.y_test),
                epochs='ten',
                batch_size=self.BATCH_SIZE,
                callbacks=[self.earlyStoppingCallback]
            )

if __name__ == "__main__":
    unittest.main()