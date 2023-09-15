#[cfg(test)]
mod cost_utils_test {
    use crate::optimisers::{Optimisable, inertial_optimiser};
    use ndarray::prelude::*;


    struct TestFunction {}

    impl Optimisable for TestFunction {
        fn call(&mut self, x: ArrayView1<f64>) -> f64 {
            (&x*&x).sum()
        }

        fn gradient(&mut self, x: ArrayView1<f64>) -> Array1<f64> {
             x.to_owned() * 2.
        }
    }

    #[test]
    fn simple_function_test() {

        let mut f = TestFunction{};
        let mut start = Array1::ones(10) * 100.;

        let c = inertial_optimiser(&mut f, start.view());
        assert!(c.argmin.sum() == 0);
        assert!(c.n_iter < 1_000);

        start = Array1::zeros(10);
        let c = inertial_optimiser(&mut f, start.view());
        assert!(c.argmin.sum() == 0);
        assert!(c.n_iter < 100);


        start = array![1., 2., 3., 4., 100.];
        let c = inertial_optimiser(&mut f, start.view());
        assert!(c.argmin.sum() == 0);
        assert!(c.n_iter < 1_000);

    }


}