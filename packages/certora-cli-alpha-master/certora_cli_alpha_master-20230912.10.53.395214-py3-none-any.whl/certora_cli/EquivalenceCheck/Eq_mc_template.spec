using CONTRACTB as B;

// sets everything but the callee the same in two environments
function e_equivalence(env e1, env e2) {
    require e1.msg.sender == e2.msg.sender;
    require e1.block.timestamp == e2.block.timestamp;
    require e1.msg.value == e2.msg.value;
    require e1.block.number == e2.block.number;
    // require e1.msg.data == e2.msg.data;
}

rule equivalence_of_revert_conditions()
{
    bool <Fa>_<Ca>_revert;
    bool <Fb>_<Cb>_revert;
    // using this as opposed to generating input parameters is experimental
    env e_<Fa>_<Ca>; calldataarg args;
    env e_<Fb>_<Cb>;
    e_equivalence(e_<Fa>_<Ca>, e_<Fb>_<Cb>);

    <Fa>@withrevert(e_<Fa>_<Ca>, args);
    <Fa>_<Ca>_revert = lastReverted;

    B.<Fb>@withrevert(e_<Fb>_<Cb>, args);
    <Fb>_<Cb>_revert = lastReverted;

    assert(<Fa>_<Ca>_revert == <Fb>_<Cb>_revert);
}

rule equivalence_of_return_value()
{
    OUTPUTS_DEC

    env e_<Fa>_<Ca>; calldataarg args;
    env e_<Fb>_<Cb>;

    e_equivalence(e_<Fa>_<Ca>, e_<Fb>_<Cb>);

    OUTPUTS_IN_A = <Fa>(e_<Fa>_<Ca>, args);
    OUTPUTS_IN_B = B.<Fb>(e_<Fb>_<Cb>, args);

    COMPARE_OUTPUTS
}
