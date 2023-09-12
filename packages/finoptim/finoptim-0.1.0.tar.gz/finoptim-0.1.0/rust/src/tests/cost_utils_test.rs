



#[cfg(test)]
mod cost_utils_test {
    use crate::{cost_utils::{*}, pricing_models::{PricingModel, Term}};
    use approx::relative_eq;
    use ndarray::prelude::*;


    const USAGE: [[f64; 3]; 8] = [[1., 2., 3.],
        [45., 5., 16.],
        [40., 0., 16.],
        [41., 0., 86.],
        [42., 0., 76.],
        [43., 0., 46.],
        [42., 1., 46.],
        [41., 1., 36.]];

    
    
    static PRICES: [[f64; 3]; 3] = [[5., 10., 8.],
                                    [4., 7.5, 6.],
                                    [3., 5.5, 4.5]];
    
    static LEVELS: [f64; 4] = [14., 41.,  0., 34.];

    #[test]
    fn cost_scalar_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);
        
        let mut dump = usage.clone();

        let c = cost_scalar(usage.view(), prices.view(), levels.view(), &mut dump);
        println!("{c}");
        assert!(c == 55680.);
    }

    #[test]
    fn cost_test() {

        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);

        let mut dump = usage.clone();


        let (i, j) = usage.dim();
        let two_dim_levels = Array2::zeros((i, j  + 1)) + &levels;
        let c = cost(usage.view(), prices.view(), two_dim_levels.view(), &mut dump);
        println!("{c}");
        assert!(c == 3281.8333333333335);
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
        models.push(PricingModel::Reservations(Term::OneYear, prices.slice(s![2, ..]), current_levels.view()));
        models.push(PricingModel::SavingsPlans(Term::OneYear, prices.slice(s![1, ..]), current_levels.slice(s![.., 0])));
        models.push(PricingModel::OnDemand(prices.slice(s![0, ..])));

        models.sort();

        let x = array![41.,  0., 34., 14.];
        let c = cost_final(usage.view(), &models, x.view(), false, &mut dump);

        let two_dim_levels = Array2::zeros((i, j  + 1)) + &levels;
        let cp = cost(usage.view(), prices.view(), two_dim_levels.view(), &mut dump);

        assert!(c == cp);


        models.push(PricingModel::Reservations(Term::ThreeYears, prices.slice(s![2, ..]), current_levels.view()));
        models.push(PricingModel::SavingsPlans(Term::ThreeYears, prices.slice(s![1, ..]), current_levels.slice(s![.., 0])));
        models.sort();

        let x = array![1., 0., 4., 40.,  0., 30., 4., 10.];
        let c = cost_final(usage.view(), &models, x.view(), false, &mut dump);

        println!("{c}");
        assert!(relative_eq!(c, cp, epsilon = f64::EPSILON));

    }

    #[test]
    fn coverage_test() {
        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = arr1(&LEVELS);

        
        let (i, j) = usage.dim();
        let two_dim_levels = Array2::zeros((i, j  + 1)) + &levels;
        let c = coverage(usage.view(), prices.view(), two_dim_levels.view());
        println!("{c}");
        assert!(c == 0.9500200080032012);
    }

}