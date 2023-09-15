#[cfg(test)]
mod cost_utils_test {
    use crate::{
        cost_utils::*,
        pricing_models::{PricingModel, Term},
    };
    use approx::relative_eq;
    use ndarray::prelude::*;

    const USAGE: [[f64; 3]; 11] = [
        [1., 2., 3.],
        [45., 5., 16.],
        [40., 0., 16.],
        [41., 0., 86.],
        [42., 0., 76.],
        [40., 0., 17.],
        [46., 0., 86.],
        [42., 0., 76.],
        [43., 0., 46.],
        [42., 1., 46.],
        [41., 1., 36.],
    ];

    static PRICES: [[f64; 3]; 3] = [[5., 10., 8.], [4., 7.5, 6.], [3., 5.5, 4.5]];

    static GENERAL_PRICES: [[f64; 3]; 5] = [
        [5., 10., 8.],   // OD
        [4., 7.5, 6.],   // SP3Y
        [3., 5.5, 4.5],  // RI3Y
        [4.5, 8.5, 7.2], // SP1Y
        [3.8, 6.5, 5.5], // RI1Y
    ];

    static LEVELS: [f64; 4] = [7., 30., 0., 31.];

    static GENERAL_LEVELS: [f64; 8] = [30., 0., 31., 7., 0., 7., 3., 1.];

    #[test]
    fn cost_scalar_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);

        let mut dump = usage.clone();

        let c = cost_scalar(usage.view(), prices.view(), levels.view(), &mut dump);
        println!("cost_scalar_test output : {c}");
        assert!(c == 63412.);
    }

    #[test]
    fn cost_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);

        let mut dump = usage.clone();

        let (i, j) = usage.dim();
        let two_dim_levels = Array2::zeros((i, j + 1)) + &levels;
        let c = cost(
            usage.view(),
            prices.view(),
            two_dim_levels.view(),
            &mut dump,
        );
        println!("cost_test output : {c}");
        assert!(c == 5084.666666666666);
    }

    #[test]
    fn cost_final_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);

        let mut dump = usage.clone();

        let (i, j) = usage.dim();
        let current_levels = Array2::zeros((i, j));
        let mut models = Vec::with_capacity(3);
        models.push(PricingModel::Reservations(
            Term::OneYear,
            prices.slice(s![2, ..]),
            current_levels.view(),
        ));
        models.push(PricingModel::SavingsPlans(
            Term::OneYear,
            prices.slice(s![1, ..]),
            current_levels.slice(s![.., 0]),
        ));
        models.push(PricingModel::OnDemand(prices.slice(s![0, ..])));

        models.sort();

        let x = arr1(&GENERAL_LEVELS);
        let c = cost_final(usage.view(), &models, x.slice(s![..4]), false, &mut dump);

        let two_dim_levels = Array2::zeros((i, j + 1)) + &levels;
        let cp = cost(
            usage.view(),
            prices.view(),
            two_dim_levels.view(),
            &mut dump,
        );
        println!("final cost test  : {c} != {cp}");
        assert!(relative_eq!(c, cp, epsilon = f64::EPSILON));

        models.push(PricingModel::Reservations(
            Term::ThreeYears,
            prices.slice(s![2, ..]),
            current_levels.view(),
        ));
        models.push(PricingModel::SavingsPlans(
            Term::ThreeYears,
            prices.slice(s![1, ..]),
            current_levels.slice(s![.., 0]),
        ));
        models.sort();

        let x = array![1., 0., 4., 40., 0., 30., 4., 10.];
        let c = cost_final(usage.view(), &models, x.view(), false, &mut dump);

        println!("cost_final_test output : {c} != {cp}");
        assert!(relative_eq!(c, 4898., epsilon = f64::EPSILON));
    }

    #[test]
    fn coverage_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);

        let (i, j) = usage.dim();
        let two_dim_levels = Array2::zeros((i, j + 1)) + &levels;
        let c = coverage(usage.view(), prices.view(), two_dim_levels.view());
        println!("coverage_test output : {c}");
        assert!(c == 0.7174656619101063);
    }

    #[test]
    fn final_coverage_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&GENERAL_PRICES);
        let x = arr1(&GENERAL_LEVELS);
        let levels = arr1(&LEVELS);

        let (i, j) = usage.dim();
        let two_dim_levels = Array2::zeros((i, j + 1)) + &levels;
        let c = coverage(usage.view(), prices.slice(s![..3, ..]), two_dim_levels.view());
        println!("final_coverage_test  : {c}");
        assert!(c == 0.7174656619101063);

        let null_base_level = Array2::zeros((i, j));


        let mut models = vec![PricingModel::OnDemand(prices.slice(s![0, ..])),
                            PricingModel::Reservations(Term::ThreeYears, prices.slice(s![2, ..]), null_base_level.view()),
                            PricingModel::SavingsPlans(Term::ThreeYears, prices.slice(s![1, ..]), null_base_level.slice(s![.., 0]))];
        models.sort();


        let cp = final_coverage(usage.view(), &models, x.slice(s![..4]), false, &mut usage.clone());
        println!("final_coverage_test  : {c} != {cp}");
        assert!(relative_eq!(c, cp, epsilon = f64::EPSILON));

        models.push(PricingModel::Reservations(Term::OneYear, prices.slice(s![4, ..]), null_base_level.view()));
        models.push(PricingModel::SavingsPlans(Term::OneYear, prices.slice(s![3, ..]), null_base_level.slice(s![.., 0])));
        models.sort();

        let c = final_coverage(usage.view(), &models, x.view(), false, &mut usage.clone());
        println!("final_coverage_general_test output : {c}");
        assert!(c == 0.8710578133236085);
    }
}
