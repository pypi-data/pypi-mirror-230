# import pytest
# import numpy as np
# from coreframe import CoreFrame
# import string
# import random

# # using pytest

# # I need nd dataset with different dtypes of dtimes

# # I need table dataset with different dtypes of dtimes

# # I need tests that will supply all combinations of the dtypes of dtimes

# @pytest.fixture(scope="session")
# def example_3d_array_and_dtimes():
#     nd_data = np.random.rand(500, 100, 100)
#     base = np.datetime64("2001-03-21", 'D')
#     dtimes = np.asarray([base + np.timedelta64(x, 'D') for x in range(500)])
#     return nd_data, dtimes

# # @pytest.fixture(scope="session")
# # def example_2d_array_and_dtimes_and_column_names():
# #     alphabet = string.ascii_lowercase + string.digits

# #     nd_data = np.random.rand(500, 100)
# #     base = np.datetime64("2001-03-21", 'D')
# #     dtimes = np.asarray([base + np.timedelta64(x, 'D') for x in range(500)])
# #     col_names = []
# #     for _ in range(100):
# #         word = ''.join(random.choices(alphabet, k=8)) 
# #         while word in col_names:
# #             word = ''.join(random.choices(alphabet, k=8)) 
# #         col_names.append(word)

# #     return nd_data, dtimes, col_names

# # TESTS that test constructor restrictions
# def test_constructor_nd_simple(example_3d_array_and_dtimes):
#     data, dtimes = example_3d_array_and_dtimes
#     try:
#         CoreFrame(data, dtimes)
#     except Exception as exc:
#         assert  False, f"Exception  was  raised {exc}"

# # def test_constructor_table_simple(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     try:
# #         print(col_names)
# #         CoreFrame(data, dtimes, col_names=col_names)
# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # def test_constructor_table_wrong_n_col_names(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     with pytest.raises(Exception) as e_info:
# #         CoreFrame(data, dtimes=dtimes, col_names=col_names[:len(col_names)/2])

# # def test_constructor_table_duplicate_col_names(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     a = random.randint(0, len(col_names) - 1)
# #     b = random.randint(0, len(col_names) - 1)
# #     while b == a:
# #        b = random.randint(0, len(col_names))

# #     new_col_names = col_names.copy()
# #     new_col_names[a] = new_col_names[b]
    
# #     with pytest.raises(Exception) as e_info:
# #         CoreFrame(data, dtimes=dtimes, col_names=new_col_names)

# # def test_constructor_table_wrong_dimensions(example_3d_array_and_dtimes, example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes = example_3d_array_and_dtimes
# #     _, _, col_names = example_2d_array_and_dtimes_and_column_names
# #     print(data.shape)
# #     with pytest.raises(Exception) as e_info:
# #         CoreFrame(data, dtimes=dtimes, col_names=col_names)

# def test_slicing_single_nd_data(example_3d_array_and_dtimes):
#     data, dtimes = example_3d_array_and_dtimes
#     try:
#         cf = CoreFrame(data, dtimes)
#         a = random.randint(0, len(dtimes) - 1)
#         b = min(a + 10, len(dtimes) - 1)
#         sliced_cf = cf[a:b]
#         assert sliced_cf.shape[0] == len(sliced_cf.dtimes), "Different length of data and dtimes"
#         single_cf = cf[a]
#         # TODO: add setting check
#     except Exception as exc:
#         assert  False, f"Exception  was  raised {exc}"

# def test_slicing_multi_nd_data(example_3d_array_and_dtimes):
#     data, dtimes = example_3d_array_and_dtimes
#     try:
#         cf = CoreFrame(data, dtimes)
#         a = random.randint(0, len(dtimes) - 1)
#         b = min(a + 10, len(dtimes) - 1)
#         sliced_cf = cf[a:b, 4:44, 3:33]
#         assert sliced_cf.shape[0] == len(sliced_cf.dtimes), "Different length of data and dtimes"
#         sliced_cf = cf[a, 34:44, 23:33]
#         # assert  sliced_cf.shape == (1, 10, 10) # TODO this behavior must be decided       
#         single_cf = cf[a, 44, 33]
#         print(single_cf)
#         # TODO: add setting check

#     except Exception as exc:
#         assert  False, f"Exception  was  raised {exc}"

# # def test_slicing_single_table_data(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     try:
# #         cf = CoreFrame(data, dtimes, col_names=col_names)
# #         a = random.randint(0, len(dtimes) - 1)
# #         b = min(a + 10, len(dtimes) - 1)
# #         sliced_cf = cf[a:b]
# #         assert sliced_cf.shape[0] == len(sliced_cf.dtimes), "Different length of data and dtimes"
# #         single_cf = cf[a]
# #         # TODO: add setting check
# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # def test_slicing_multi_table_data(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     try:
# #         cf = CoreFrame(data, dtimes, col_names=col_names)
# #         a = random.randint(0, len(dtimes) - 1)
# #         b = min(a + 10, len(dtimes) - 1)
# #         sliced_cf = cf[a:b, 4:44]
# #         assert sliced_cf.shape[0] == len(sliced_cf.dtimes), "Different length of data and dtimes"
# #         sliced_cf = cf[a, 34:44]
# #         # assert  sliced_cf.shape == (1, 10, 10) # TODO this behavior must be decided       
# #         single_cf = cf[a, 44]
# #         print(single_cf)
# #         # TODO: add setting check

# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # def test_slicing_single_columns_present(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     try:
# #         cf = CoreFrame(data, dtimes, col_names=col_names)
# #         a = random.randint(0, len(col_names) - 1)
# #         cf[col_names[a]]
# #         # TODO: add setting check

# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # def test_slicing_single_columns_absent(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     cf = CoreFrame(data, dtimes, col_names=col_names)
# #     with pytest.raises(Exception) as e_info:
# #         cf["AAAAAAAAAAAAAA"]

# # def test_slicing_mutli_columns_present(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     try:
# #         cf = CoreFrame(data, dtimes, col_names=col_names)
# #         a = random.randint(0, len(col_names) - 1)
# #         b = min(a + 10, len(col_names) - 1)
# #         assert cf[[col_names[a], col_names[b]]].shape == (len(dtimes), 2)
# #         # TODO: add setting check?

# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # def test_slicing_mutli_columns_absent(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     cf = CoreFrame(data, dtimes, col_names=col_names)
# #     with pytest.raises(Exception) as e_info:
# #         cf[["AAAAAAAAAAAAAA", col_names[0], "BBBBBBBBBBBBB"]]

# # def test_slicing_mutli_columns_duplicates(example_2d_array_and_dtimes_and_column_names):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     cf = CoreFrame(data, dtimes, col_names=col_names)
# #     with pytest.raises(Exception) as e_info:
# #         cf[[col_names[0], col_names[0], ]]
        
# # iter_by_time tests

# @pytest.mark.parametrize("num", [1, 7, 12])
# @pytest.mark.parametrize("t_type_fn",['s', 'D', 'W', 'M', 'Y'])
# @pytest.mark.parametrize("t_type_cf", ['s', 'D', 'W', 'M', 'Y'])
# def test_iter_by_time_permutations_nd_data(example_3d_array_and_dtimes, num, t_type_cf, t_type_fn):
#     data, dtimes = example_3d_array_and_dtimes
#     dtimes = dtimes.astype(f"datetime64[{t_type_cf}]")
#     itert = str(num) + t_type_fn
#     try:
#         cf = CoreFrame(data, dtimes)
#         print(cf.iter_by_time(itert))

#     except Exception as exc:
#         assert  False, f"Exception  was  raised {exc}"


# # @pytest.mark.parametrize("num", [1, 7, 12])
# # @pytest.mark.parametrize("t_type_fn",['s', 'D', 'W', 'M', 'Y'])
# # @pytest.mark.parametrize("t_type_cf", ['s', 'D', 'W', 'M', 'Y'])
# # def test_iter_by_time_permutations_table_data(example_2d_array_and_dtimes_and_column_names, num, t_type_cf, t_type_fn):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     dtimes = dtimes.astype(f"datetime64[{t_type_cf}]")
# #     itert = str(num) + t_type_fn
# #     try:
# #         cf = CoreFrame(data, dtimes, col_names=col_names)
# #         print(cf.iter_by_time(itert))

# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # between tests



# # split tests

# @pytest.mark.parametrize("num", [1, 7, 12])
# @pytest.mark.parametrize("t_type_fn",['s', 'D', 'W', 'M', 'Y'])
# @pytest.mark.parametrize("t_type_cf", ['s', 'D', 'W', 'M', 'Y'])
# def test_split_permutations_nd_data(example_3d_array_and_dtimes, num, t_type_cf, t_type_fn):
#     data, dtimes = example_3d_array_and_dtimes
#     dtimes = dtimes.astype(f"datetime64[{t_type_cf}]")
#     itert = str(num) + t_type_fn
#     try:
#         cf = CoreFrame(data, dtimes)
#         print(cf.split(itert))

#     except Exception as exc:
#         assert  False, f"Exception  was  raised {exc}"


# # @pytest.mark.parametrize("num", [1, 7, 12])
# # @pytest.mark.parametrize("t_type_fn",['s', 'D', 'W', 'M', 'Y'])
# # @pytest.mark.parametrize("t_type_cf", ['s', 'D', 'W', 'M', 'Y'])
# # def test_split_permutations_table_data(example_2d_array_and_dtimes_and_column_names, num, t_type_cf, t_type_fn):
# #     data, dtimes, col_names = example_2d_array_and_dtimes_and_column_names
# #     dtimes = dtimes.astype(f"datetime64[{t_type_cf}]")
# #     itert = str(num) + t_type_fn
# #     try:
# #         cf = CoreFrame(data, dtimes, col_names=col_names)
# #         print(cf.split(itert))

# #     except Exception as exc:
# #         assert  False, f"Exception  was  raised {exc}"

# # def test_
