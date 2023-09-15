



#[cfg(test)]
mod cost_utils_test {
    use std::env;
    use ndarray::{prelude::*, Zip};

    use crate::optimisers::Optimisable;
    use crate::pricing_models::{PricingModel, Term};
    use crate::pre_processing::CostFunction;


    const USAGE: [[f64; 3]; 12] = [[1., 2., 3.],
        [45., 5.1, 16.],
        [40., 0.9, 16.],
        [41., 15., 86.],
        [42., 10., 76.],
        [43., 0.1, 46.],
        [42., 1.1, 46.],
        [41., 23., 86.],
        [42., 0.5, 76.],
        [43., 0.1, 46.],
        [42., 1.1, 46.],
        [41., 1.0, 36.]];

    
    
    static PRICES: [[f64; 3]; 5] = [[5., 10., 8.],
                                    [3.5, 7.8, 7.],
                                    [3., 7.5, 6.],
                                    [3.3, 7., 5.],
                                    [3., 5., 4.5]];
    
    static LEVELS: [f64; 4] = [14., 41.,  0., 34.];


    #[test]
    fn gradiant_test() {
        // env::set_var("RUST_BACKTRACE", "1");

        let usage = arr2(&USAGE);
        let prices = arr2(&PRICES);
        let levels = Array2::zeros(usage.dim());

        let mut models = Vec::with_capacity(5);
        models.push(PricingModel::Reservations(Term::OneYear, prices.slice(s![3, ..]), levels.view()));
        models.push(PricingModel::Reservations(Term::ThreeYears, prices.slice(s![4, ..]), levels.view()));
        models.push(PricingModel::SavingsPlans(Term::OneYear, prices.slice(s![1, ..]), levels.slice(s![.., 0])));
        models.push(PricingModel::SavingsPlans(Term::ThreeYears, prices.slice(s![2, ..]), levels.slice(s![.., 0])));
        models.push(PricingModel::OnDemand(prices.slice(s![0, ..])));
        
        models.sort();

        let mut function = CostFunction::new(usage, &models, false, false);

        let x = array![5., 5., 7., 4.2, 0., 6., 4., 0.01];
        let g = function.gradient(x.view());

        
        let mut h = Array2::from_diag(&function.steps);
        h += &x;
        let c = function.call(x.view());
        let mut k = h.map_axis_mut(Axis(1), |row| {
            println!(">>>> {:?}", row);
            function.call(row.view()) - c
        });
        Zip::from(&mut k).and(&x).for_each(|z, &y| {if y < *z {*z = y}});
        k /= &function.steps;



        println!("calling f manually : \n {:?}", k);
        println!("grad function : \n {:?}", g);

        assert!(k == g);

    }


}