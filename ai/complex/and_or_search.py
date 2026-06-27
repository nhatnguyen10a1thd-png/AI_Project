# ai/complex/and_or_search.py
import time
import copy
from ai.search_result import SearchResult


def and_or_solve(start_state, rules, max_depth=8):
    """
    AND-OR Graph Search for Squirrel Go Nuts.

    Môi trường không xác định:
    - Một hành động có thể tạo ra nhiều kết quả.
    - Ở đây mô phỏng Slippery Mode:
        Outcome 1: đi/trượt 1 lần theo action.
        Outcome 2: nếu sau outcome 1 vẫn đi tiếp được thì trượt thêm 1 lần nữa.

    Kết quả trả về:
    - Conditional plan tree.
    - Sample path để UI có thể demo tuyến tính.
    """

    FAILURE = None
    GOAL = {"type": "goal"}

    start_time = time.time()

    steps = [
        (
            0,
            "Bắt đầu AND-OR Graph Search: môi trường không xác định, trượt 1 hoặc 2 ô",
            start_state,
        )
    ]

    step_num = [1]
    visited_count = [0]
    generated_count = [0]

    # =========================
    # Safe action application
    # =========================
    def safe_apply_action(state, action):
        """
        Đảm bảo apply_action không làm hỏng state gốc.

        Nếu rules.apply_action() đã trả state mới thì vẫn ổn.
        Nếu rules.apply_action() lỡ mutate state truyền vào,
        ta vẫn bảo vệ state gốc bằng deepcopy trước.
        """

        state_copy = copy.deepcopy(state)
        result = rules.apply_action(state_copy, action)

        # Nếu apply_action trả về None, xem state_copy là state sau khi bị mutate.
        if result is None:
            return state_copy

        # Deepcopy thêm một lần để tránh các nhánh AND dùng chung object.
        return copy.deepcopy(result)

    # =========================
    # Non-deterministic outcomes
    # =========================
    def get_outcomes(state, action):
        """
        Sinh tất cả kết quả có thể xảy ra của một action.

        Outcome 1:
            Di chuyển/trượt bình thường 1 lần.

        Outcome 2:
            Nếu sau Outcome 1 vẫn có thể đi tiếp cùng hướng,
            quân trượt thêm 1 lần nữa.
        """

        outcomes = {}

        # Outcome 1: đi 1 lần
        st1 = safe_apply_action(state, action)
        outcomes[st1.encode()] = st1

        # Outcome 2: trượt thêm 1 lần nếu còn đi được
        pid, direction = action

        if rules.can_move(st1, pid, direction):
            st2 = safe_apply_action(st1, action)
            outcomes[st2.encode()] = st2

        return list(outcomes.values())

    # =========================
    # OR search
    # =========================
    def or_search(state, path, depth):
        """
        OR node:
        Agent được quyền chọn một action.

        Nếu có ít nhất một action mà mọi outcome đều giải được,
        thì action đó được chọn.
        """

        visited_count[0] += 1

        if state.is_goal():
            steps.append(
                (
                    step_num[0],
                    f"OR: Gặp trạng thái goal ở độ sâu {depth}",
                    state,
                )
            )
            step_num[0] += 1
            return GOAL

        if depth >= max_depth:
            steps.append(
                (
                    step_num[0],
                    f"OR: Dừng vì đạt giới hạn độ sâu max_depth={max_depth}",
                    state,
                )
            )
            step_num[0] += 1
            return FAILURE

        state_code = state.encode()

        if state_code in path:
            steps.append(
                (
                    step_num[0],
                    "OR: Phát hiện chu trình, trạng thái này đã nằm trên path hiện tại",
                    state,
                )
            )
            step_num[0] += 1
            return FAILURE

        # Không dùng visited global.
        # Path chỉ là đường đi từ gốc đến node hiện tại.
        new_path = path | {state_code}

        legal_actions = rules.legal_actions(state)

        steps.append(
            (
                step_num[0],
                f"OR: Mở rộng trạng thái ở độ sâu {depth}, có {len(legal_actions)} action hợp lệ",
                state,
            )
        )
        step_num[0] += 1

        # OR branch: thử từng action
        for action in legal_actions:
            outcomes_list = get_outcomes(state, action)
            generated_count[0] += len(outcomes_list)

            pid, direction = action

            steps.append(
                (
                    step_num[0],
                    f"OR: Thử action ({pid}, {direction}) -> sinh {len(outcomes_list)} outcome AND",
                    state,
                )
            )
            step_num[0] += 1

            # Log đủ tất cả outcomes
            for idx, out_state in enumerate(outcomes_list, start=1):
                steps.append(
                    (
                        step_num[0],
                        f"AND outcome {idx}/{len(outcomes_list)} của action ({pid}, {direction})",
                        out_state,
                    )
                )
                step_num[0] += 1

            subplan = and_search(
                states=outcomes_list,
                path=new_path,
                depth=depth + 1,
                action=action,
            )

            # Nếu tất cả outcome đều có plan, chọn action này
            if subplan is not FAILURE:
                steps.append(
                    (
                        step_num[0],
                        f"OR: Chấp nhận action ({pid}, {direction}) vì mọi outcome đều giải được",
                        state,
                    )
                )
                step_num[0] += 1

                return {
                    "type": "action",
                    "action": action,
                    "branches": subplan,
                }

            steps.append(
                (
                    step_num[0],
                    f"OR: Loại action ({pid}, {direction}) vì có ít nhất một outcome thất bại",
                    state,
                )
            )
            step_num[0] += 1

        return FAILURE

    # =========================
    # AND search
    # =========================
    def and_search(states, path, depth, action):
        """
        AND node:
        Môi trường có thể trả về nhiều outcome.

        Một action chỉ thành công nếu TẤT CẢ outcome đều có plan đi tới goal.
        """

        branches = {}

        pid, direction = action

        steps.append(
            (
                step_num[0],
                f"AND: Kiểm tra tất cả outcome của action ({pid}, {direction})",
                states[0] if states else None,
            )
        )
        step_num[0] += 1

        for idx, out_state in enumerate(states, start=1):
            steps.append(
                (
                    step_num[0],
                    f"AND: Gọi OR_SEARCH cho outcome {idx}/{len(states)}",
                    out_state,
                )
            )
            step_num[0] += 1

            subplan = or_search(out_state, path, depth)

            if subplan is FAILURE:
                steps.append(
                    (
                        step_num[0],
                        f"AND: Outcome {idx}/{len(states)} thất bại -> action không dùng được",
                        out_state,
                    )
                )
                step_num[0] += 1
                return FAILURE

            branches[out_state.encode()] = subplan

        steps.append(
            (
                step_num[0],
                f"AND: Tất cả {len(states)} outcome đều có plan",
                states[0] if states else None,
            )
        )
        step_num[0] += 1

        return branches

    # =========================
    # Run algorithm
    # =========================
    result_plan = or_search(start_state, path=set(), depth=0)
    solved = result_plan is not FAILURE

    # =========================
    # Extract sample linear path
    # =========================
    sample_path = []

    if solved and isinstance(result_plan, dict):
        curr_plan = result_plan
        curr_state = start_state

        while isinstance(curr_plan, dict) and curr_plan.get("type") == "action":
            act = curr_plan["action"]
            sample_path.append(act)

            outcomes = get_outcomes(curr_state, act)

            if not outcomes:
                break

            # Chọn outcome đầu tiên làm đường demo tuyến tính cho visualizer
            curr_state = outcomes[0]
            curr_plan = curr_plan["branches"].get(curr_state.encode())

    # =========================
    # Return result
    # =========================
    extra_info = {
        "plan_tree": str(result_plan),
        "note": (
            "AND-OR Search dùng Slippery Mode: mỗi action có thể sinh nhiều outcome. "
            "Sample path chỉ là một nhánh đại diện để UI chạy demo tuyến tính."
        ),
    }

    return SearchResult(
        algorithm="AND-OR Search",
        solved=solved,
        path=sample_path,
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra=extra_info,
    )
