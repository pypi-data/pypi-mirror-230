def create_params(**kwargs):

    ### 序列设置
    industry_effective = [] if 'industry_effective' not in kwargs else kwargs[
        'industry_effective']

    industry_invalid = [] if 'industry_invalid' not in kwargs else kwargs[
        'industry_invalid']

    riskstyle = [] if 'riskstyle' not in kwargs else kwargs['riskstyle']

    ### 通用参数设置
    weights_bandwidth = 0.1 if 'weights_bandwidth' not in kwargs else kwargs[
        'weights_bandwidth']

    method = 'fmv' if 'method' not in kwargs else kwargs['method']

    turn_over_target = 1.0 if 'turn_over_target' not in kwargs else kwargs[
        'turn_over_target']

    target_vol = 0.1 if 'target_vol' not in kwargs else kwargs['target_vol']

    lbound = 0. if 'lbound' not in kwargs else kwargs['lbound']

    ubound = 0.04 if 'ubound' not in kwargs else kwargs['ubound']

    is_benchmark = 0 if 'is_benchmark' not in kwargs else kwargs['is_benchmark']

    ### benchmark 区间设置
    benchmark_boundary = 'relative' if 'benchmark_boundary' not in kwargs else kwargs[
        'benchmark_boundary']

    benchmark_lower = 1.001 if 'benchmark_lower' not in kwargs else kwargs[
        'benchmark_lower']
    benchmark_upper = 0.8 if 'benchmark_upper' not in kwargs else kwargs[
        'benchmark_upper']

    #### total 区间设置
    total_boundary = 'relative' if 'total_boundary' not in kwargs else kwargs[
        'total_boundary']
    total_lower = 0.001 if 'total_lower' not in kwargs else kwargs[
        'total_lower']
    total_upper = 0.01 if 'total_upper' not in kwargs else kwargs['total_upper']

    #### 上限行业区间设置
    effective_industry_boundary = 'absolute' if 'effective_industry_boundary' not in kwargs else kwargs[
        'effective_industry_boundary']
    effective_industry_lower = 0.0 if 'effective_industry_lower' not in kwargs else kwargs[
        'effective_industry_lower']
    effective_industry_upper = 0.20 if 'effective_industry_upper' not in kwargs else kwargs[
        'effective_industry_upper']

    #### 下限行业区间设置
    invalid_industry_boundary = 'absolute' if 'invalid_industry_boundary' not in kwargs else kwargs[
        'invalid_industry_boundary']
    invalid_industry_lower = 0.0 if 'invalid_industry_lower' not in kwargs else kwargs[
        'invalid_industry_lower']
    invalid_industry_upper = 0.20 if 'invalid_industry_upper' not in kwargs else kwargs[
        'invalid_industry_upper']

    riskstyle_boundary = 'absolute' if 'riskstyle_boundary' not in kwargs else kwargs[
        'riskstyle_boundary']
    riskstyle_lower = 0.0 if 'riskstyle_lower' not in kwargs else kwargs[
        'riskstyle_lower']
    riskstyle_upper = 0.20 if 'riskstyle_upper' not in kwargs else kwargs[
        'riskstyle_upper']

    neutralized_styles = None if 'neutralized_styles' not in kwargs else kwargs[
        'neutralized_styles']

    other_boundary = 'absolute' if 'other_boundary' not in kwargs else kwargs[
        'other_boundary']

    params = {}
    params['industry'] = {}
    params['riskstyle'] = {}
    ### 序列设置
    params['industry']['effective'] = industry_effective
    params['industry']['invalid'] = industry_invalid
    params['riskstyle'] = riskstyle

    ### 通用参数设置
    params['setting_params'] = {}
    params['setting_params']['weights_bandwidth'] = weights_bandwidth
    params['setting_params']['method'] = method
    params['setting_params']['turn_over_target'] = turn_over_target
    params['setting_params']['target_vol'] = target_vol
    params['setting_params']['lbound'] = lbound
    params['setting_params']['ubound'] = ubound
    params['setting_params']['is_benchmark'] = is_benchmark

    params['setting_params']['benchmark'] = {}
    params['setting_params']['total'] = {}
    params['setting_params']['other'] = {}

    ###
    params['setting_params']['other']['boundary'] = other_boundary
    params['setting_params']['other']['lower'] = 0.0
    params['setting_params']['other']['upper'] = 0.0

    # benchmark 区间设置
    params['setting_params']['benchmark']['boundary'] = benchmark_boundary
    params['setting_params']['benchmark']['lower'] = benchmark_lower
    params['setting_params']['benchmark']['upper'] = benchmark_upper

    # total 区间设置   条件6
    params['setting_params']['total']['boundary'] = total_boundary
    params['setting_params']['total']['lower'] = total_lower
    params['setting_params']['total']['upper'] = total_upper

    ### 此处考虑行业择时
    params['setting_params']['effective_industry'] = {}
    params['setting_params']['invalid_industry'] = {}

    #### effective_industry 上限行业区间设置
    params['setting_params']['effective_industry'][
        'boundary'] = effective_industry_boundary
    params['setting_params']['effective_industry'][
        'lower'] = effective_industry_lower
    params['setting_params']['effective_industry'][
        'upper'] = effective_industry_upper

    #### invalid_industry 下限行业区间设置
    params['setting_params']['invalid_industry'][
        'boundary'] = invalid_industry_boundary
    params['setting_params']['invalid_industry'][
        'lower'] = invalid_industry_lower
    params['setting_params']['invalid_industry'][
        'upper'] = invalid_industry_upper

    ### riskstyle 风格设置
    params['setting_params']['riskstyle'] = {}
    params['setting_params']['riskstyle']['boundary'] = riskstyle_boundary
    params['setting_params']['riskstyle']['lower'] = riskstyle_lower
    params['setting_params']['riskstyle']['upper'] = riskstyle_upper

    params['setting_params']['neutralized_styles'] = neutralized_styles
    return params