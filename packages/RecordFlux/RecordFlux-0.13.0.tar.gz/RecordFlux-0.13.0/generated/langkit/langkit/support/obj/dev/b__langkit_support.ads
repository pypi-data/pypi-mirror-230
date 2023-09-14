pragma Warnings (Off);
pragma Ada_95;
with System;
with System.Parameters;
with System.Secondary_Stack;
package langkit_supportmain is

   procedure langkit_supportinit;
   pragma Export (C, langkit_supportinit, "langkit_supportinit");
   pragma Linker_Constructor (langkit_supportinit);

   procedure langkit_supportfinal;
   pragma Export (C, langkit_supportfinal, "langkit_supportfinal");
   pragma Linker_Destructor (langkit_supportfinal);

   type Version_32 is mod 2 ** 32;
   u00001 : constant Version_32 := 16#51412d59#;
   pragma Export (C, u00001, "langkit_support__adalog__debugB");
   u00002 : constant Version_32 := 16#02009bfa#;
   pragma Export (C, u00002, "langkit_support__adalog__debugS");
   u00003 : constant Version_32 := 16#8aa64106#;
   pragma Export (C, u00003, "langkit_support__adalog__generic_main_supportB");
   u00004 : constant Version_32 := 16#1b831e6d#;
   pragma Export (C, u00004, "langkit_support__adalog__generic_main_supportS");
   u00005 : constant Version_32 := 16#a069c901#;
   pragma Export (C, u00005, "langkit_support__adalog__logic_varB");
   u00006 : constant Version_32 := 16#320ada8a#;
   pragma Export (C, u00006, "langkit_support__adalog__logic_varS");
   u00007 : constant Version_32 := 16#1e6104af#;
   pragma Export (C, u00007, "langkit_support__adalog__main_supportB");
   u00008 : constant Version_32 := 16#bc87f5b3#;
   pragma Export (C, u00008, "langkit_support__adalog__main_supportS");
   u00009 : constant Version_32 := 16#bbe81320#;
   pragma Export (C, u00009, "langkit_support__adalog__solverB");
   u00010 : constant Version_32 := 16#b78a4d1b#;
   pragma Export (C, u00010, "langkit_support__adalog__solverS");
   u00011 : constant Version_32 := 16#01e47c01#;
   pragma Export (C, u00011, "langkit_support__adalog__solver_interfaceB");
   u00012 : constant Version_32 := 16#b8e98259#;
   pragma Export (C, u00012, "langkit_support__adalog__solver_interfaceS");
   u00013 : constant Version_32 := 16#d3a4264b#;
   pragma Export (C, u00013, "langkit_support__adalogS");
   u00014 : constant Version_32 := 16#a11eb54d#;
   pragma Export (C, u00014, "langkit_support__array_utilsB");
   u00015 : constant Version_32 := 16#f3d0463b#;
   pragma Export (C, u00015, "langkit_support__array_utilsS");
   u00016 : constant Version_32 := 16#149bb95c#;
   pragma Export (C, u00016, "langkit_support__boxesB");
   u00017 : constant Version_32 := 16#a741d012#;
   pragma Export (C, u00017, "langkit_support__boxesS");
   u00018 : constant Version_32 := 16#370ac9db#;
   pragma Export (C, u00018, "langkit_support__bump_ptrB");
   u00019 : constant Version_32 := 16#65652129#;
   pragma Export (C, u00019, "langkit_support__bump_ptrS");
   u00020 : constant Version_32 := 16#e3f98dc7#;
   pragma Export (C, u00020, "langkit_support__bump_ptr_vectorsB");
   u00021 : constant Version_32 := 16#f21d0cb1#;
   pragma Export (C, u00021, "langkit_support__bump_ptr_vectorsS");
   u00022 : constant Version_32 := 16#21a3a64c#;
   pragma Export (C, u00022, "langkit_support__cheap_setsB");
   u00023 : constant Version_32 := 16#15858c5b#;
   pragma Export (C, u00023, "langkit_support__cheap_setsS");
   u00024 : constant Version_32 := 16#b881c93a#;
   pragma Export (C, u00024, "langkit_support__diagnostics__outputB");
   u00025 : constant Version_32 := 16#589b0e88#;
   pragma Export (C, u00025, "langkit_support__diagnostics__outputS");
   u00026 : constant Version_32 := 16#d1260a94#;
   pragma Export (C, u00026, "langkit_support__diagnosticsB");
   u00027 : constant Version_32 := 16#9538f127#;
   pragma Export (C, u00027, "langkit_support__diagnosticsS");
   u00028 : constant Version_32 := 16#ffdb8d40#;
   pragma Export (C, u00028, "langkit_support__errorsS");
   u00029 : constant Version_32 := 16#1d7b0e47#;
   pragma Export (C, u00029, "langkit_support__file_readersB");
   u00030 : constant Version_32 := 16#9d63d35f#;
   pragma Export (C, u00030, "langkit_support__file_readersS");
   u00031 : constant Version_32 := 16#d2b9d6e6#;
   pragma Export (C, u00031, "langkit_support__generic_api__analysisB");
   u00032 : constant Version_32 := 16#58843711#;
   pragma Export (C, u00032, "langkit_support__generic_api__analysisS");
   u00033 : constant Version_32 := 16#8ac40e2b#;
   pragma Export (C, u00033, "langkit_support__generic_api__introspectionB");
   u00034 : constant Version_32 := 16#35278a06#;
   pragma Export (C, u00034, "langkit_support__generic_api__introspectionS");
   u00035 : constant Version_32 := 16#11f57582#;
   pragma Export (C, u00035, "langkit_support__generic_apiB");
   u00036 : constant Version_32 := 16#ed6040d9#;
   pragma Export (C, u00036, "langkit_support__generic_apiS");
   u00037 : constant Version_32 := 16#c9012051#;
   pragma Export (C, u00037, "langkit_support__generic_bump_ptrB");
   u00038 : constant Version_32 := 16#89790d5b#;
   pragma Export (C, u00038, "langkit_support__generic_bump_ptrS");
   u00039 : constant Version_32 := 16#012b8ba0#;
   pragma Export (C, u00039, "langkit_support__hashesB");
   u00040 : constant Version_32 := 16#637eb8f4#;
   pragma Export (C, u00040, "langkit_support__hashesS");
   u00041 : constant Version_32 := 16#d29647e5#;
   pragma Export (C, u00041, "langkit_support__imagesB");
   u00042 : constant Version_32 := 16#ece27e84#;
   pragma Export (C, u00042, "langkit_support__imagesS");
   u00043 : constant Version_32 := 16#c8faf658#;
   pragma Export (C, u00043, "langkit_support__internal__analysisB");
   u00044 : constant Version_32 := 16#8645fce0#;
   pragma Export (C, u00044, "langkit_support__internal__analysisS");
   u00045 : constant Version_32 := 16#ca746d76#;
   pragma Export (C, u00045, "langkit_support__internal__conversionsS");
   u00046 : constant Version_32 := 16#382230d9#;
   pragma Export (C, u00046, "langkit_support__internal__descriptorS");
   u00047 : constant Version_32 := 16#b694038c#;
   pragma Export (C, u00047, "langkit_support__internal__introspectionB");
   u00048 : constant Version_32 := 16#c57332a6#;
   pragma Export (C, u00048, "langkit_support__internal__introspectionS");
   u00049 : constant Version_32 := 16#b6f7c8dc#;
   pragma Export (C, u00049, "langkit_support__internalS");
   u00050 : constant Version_32 := 16#f8e452f2#;
   pragma Export (C, u00050, "langkit_support__iteratorsB");
   u00051 : constant Version_32 := 16#5557ee41#;
   pragma Export (C, u00051, "langkit_support__iteratorsS");
   u00052 : constant Version_32 := 16#253b2a64#;
   pragma Export (C, u00052, "langkit_support__lexical_envsS");
   u00053 : constant Version_32 := 16#9c9d0fff#;
   pragma Export (C, u00053, "langkit_support__lexical_envs_implB");
   u00054 : constant Version_32 := 16#f5953f2d#;
   pragma Export (C, u00054, "langkit_support__lexical_envs_implS");
   u00055 : constant Version_32 := 16#4e5f7be4#;
   pragma Export (C, u00055, "langkit_support__names__mapsB");
   u00056 : constant Version_32 := 16#8e8acc12#;
   pragma Export (C, u00056, "langkit_support__names__mapsS");
   u00057 : constant Version_32 := 16#9f94b52e#;
   pragma Export (C, u00057, "langkit_support__namesB");
   u00058 : constant Version_32 := 16#3e8cb528#;
   pragma Export (C, u00058, "langkit_support__namesS");
   u00059 : constant Version_32 := 16#a40bf957#;
   pragma Export (C, u00059, "langkit_support__packratB");
   u00060 : constant Version_32 := 16#e8539af8#;
   pragma Export (C, u00060, "langkit_support__packratS");
   u00061 : constant Version_32 := 16#36d83113#;
   pragma Export (C, u00061, "langkit_support__relative_getB");
   u00062 : constant Version_32 := 16#fdc5e6fb#;
   pragma Export (C, u00062, "langkit_support__relative_getS");
   u00063 : constant Version_32 := 16#1aba2a03#;
   pragma Export (C, u00063, "langkit_support__slocsB");
   u00064 : constant Version_32 := 16#dd36fb05#;
   pragma Export (C, u00064, "langkit_support__slocsS");
   u00065 : constant Version_32 := 16#0ba179ac#;
   pragma Export (C, u00065, "langkit_support__symbols__precomputedB");
   u00066 : constant Version_32 := 16#4e916dbb#;
   pragma Export (C, u00066, "langkit_support__symbols__precomputedS");
   u00067 : constant Version_32 := 16#7c9252d5#;
   pragma Export (C, u00067, "langkit_support__symbolsB");
   u00068 : constant Version_32 := 16#c5dc52d2#;
   pragma Export (C, u00068, "langkit_support__symbolsS");
   u00069 : constant Version_32 := 16#b8b42c56#;
   pragma Export (C, u00069, "langkit_support__textB");
   u00070 : constant Version_32 := 16#ddcd2807#;
   pragma Export (C, u00070, "langkit_support__textS");
   u00071 : constant Version_32 := 16#a96cdbcf#;
   pragma Export (C, u00071, "langkit_support__token_data_handlersB");
   u00072 : constant Version_32 := 16#ffb0f663#;
   pragma Export (C, u00072, "langkit_support__token_data_handlersS");
   u00073 : constant Version_32 := 16#0960169b#;
   pragma Export (C, u00073, "langkit_support__tree_traversal_iteratorB");
   u00074 : constant Version_32 := 16#7e7b784e#;
   pragma Export (C, u00074, "langkit_support__tree_traversal_iteratorS");
   u00075 : constant Version_32 := 16#18fc3b74#;
   pragma Export (C, u00075, "langkit_support__typesS");
   u00076 : constant Version_32 := 16#2e5de5e5#;
   pragma Export (C, u00076, "langkit_support__vectorsB");
   u00077 : constant Version_32 := 16#76f1b750#;
   pragma Export (C, u00077, "langkit_support__vectorsS");
   u00078 : constant Version_32 := 16#274a0117#;
   pragma Export (C, u00078, "langkit_supportS");

   --  BEGIN ELABORATION ORDER
   --  ada%s
   --  ada.characters%s
   --  ada.characters.latin_1%s
   --  ada.wide_wide_characters%s
   --  interfaces%s
   --  system%s
   --  system.address_operations%s
   --  system.address_operations%b
   --  system.atomic_operations%s
   --  system.img_char%s
   --  system.img_char%b
   --  system.io%s
   --  system.io%b
   --  system.parameters%s
   --  system.parameters%b
   --  system.crtl%s
   --  interfaces.c_streams%s
   --  interfaces.c_streams%b
   --  system.os_primitives%s
   --  system.os_primitives%b
   --  system.spark%s
   --  system.spark.cut_operations%s
   --  system.spark.cut_operations%b
   --  system.storage_elements%s
   --  system.storage_elements%b
   --  system.return_stack%s
   --  system.stack_checking%s
   --  system.stack_checking%b
   --  system.string_hash%s
   --  system.string_hash%b
   --  system.htable%s
   --  system.htable%b
   --  system.strings%s
   --  system.strings%b
   --  system.traceback_entries%s
   --  system.traceback_entries%b
   --  system.unsigned_types%s
   --  system.utf_32%s
   --  system.utf_32%b
   --  ada.wide_wide_characters.unicode%s
   --  ada.wide_wide_characters.unicode%b
   --  system.wch_con%s
   --  system.wch_con%b
   --  system.wch_jis%s
   --  system.wch_jis%b
   --  system.wch_cnv%s
   --  system.wch_cnv%b
   --  system.compare_array_unsigned_32%s
   --  system.compare_array_unsigned_32%b
   --  system.compare_array_unsigned_8%s
   --  system.compare_array_unsigned_8%b
   --  system.concat_2%s
   --  system.concat_2%b
   --  system.concat_3%s
   --  system.concat_3%b
   --  system.concat_4%s
   --  system.concat_4%b
   --  system.concat_5%s
   --  system.concat_5%b
   --  system.concat_6%s
   --  system.concat_6%b
   --  system.traceback%s
   --  system.traceback%b
   --  ada.characters.handling%s
   --  system.atomic_operations.test_and_set%s
   --  system.case_util%s
   --  system.os_lib%s
   --  system.secondary_stack%s
   --  system.standard_library%s
   --  ada.exceptions%s
   --  system.exceptions_debug%s
   --  system.exceptions_debug%b
   --  system.soft_links%s
   --  system.val_llu%s
   --  system.val_lli%s
   --  system.val_uns%s
   --  system.val_int%s
   --  system.val_util%s
   --  system.val_util%b
   --  system.wch_stw%s
   --  system.wch_stw%b
   --  ada.exceptions.last_chance_handler%s
   --  ada.exceptions.last_chance_handler%b
   --  ada.exceptions.traceback%s
   --  ada.exceptions.traceback%b
   --  system.address_image%s
   --  system.address_image%b
   --  system.bit_ops%s
   --  system.bit_ops%b
   --  system.bounded_strings%s
   --  system.bounded_strings%b
   --  system.case_util%b
   --  system.exception_table%s
   --  system.exception_table%b
   --  ada.containers%s
   --  ada.io_exceptions%s
   --  ada.numerics%s
   --  ada.numerics.big_numbers%s
   --  ada.strings%s
   --  ada.strings.maps%s
   --  ada.strings.maps%b
   --  ada.strings.maps.constants%s
   --  interfaces.c%s
   --  interfaces.c%b
   --  system.atomic_primitives%s
   --  system.atomic_primitives%b
   --  system.exceptions%s
   --  system.exceptions.machine%s
   --  system.exceptions.machine%b
   --  ada.characters.handling%b
   --  system.atomic_operations.test_and_set%b
   --  system.exception_traces%s
   --  system.exception_traces%b
   --  system.memory%s
   --  system.memory%b
   --  system.mmap%s
   --  system.mmap.os_interface%s
   --  system.mmap%b
   --  system.mmap.unix%s
   --  system.mmap.os_interface%b
   --  system.object_reader%s
   --  system.object_reader%b
   --  system.dwarf_lines%s
   --  system.os_lib%b
   --  system.secondary_stack%b
   --  system.soft_links.initialize%s
   --  system.soft_links.initialize%b
   --  system.soft_links%b
   --  system.standard_library%b
   --  system.traceback.symbolic%s
   --  system.traceback.symbolic%b
   --  system.wid_uns%s
   --  system.img_int%s
   --  ada.exceptions%b
   --  system.img_uns%s
   --  system.dwarf_lines%b
   --  ada.assertions%s
   --  ada.assertions%b
   --  ada.characters.conversions%s
   --  ada.characters.conversions%b
   --  ada.command_line%s
   --  ada.command_line%b
   --  ada.containers.prime_numbers%s
   --  ada.containers.prime_numbers%b
   --  ada.strings.hash%s
   --  ada.strings.hash%b
   --  ada.strings.hash_case_insensitive%s
   --  ada.strings.hash_case_insensitive%b
   --  ada.strings.search%s
   --  ada.strings.search%b
   --  ada.strings.fixed%s
   --  ada.strings.fixed%b
   --  ada.strings.utf_encoding%s
   --  ada.strings.utf_encoding%b
   --  ada.strings.utf_encoding.strings%s
   --  ada.strings.utf_encoding.strings%b
   --  ada.strings.utf_encoding.wide_strings%s
   --  ada.strings.utf_encoding.wide_strings%b
   --  ada.strings.utf_encoding.wide_wide_strings%s
   --  ada.strings.utf_encoding.wide_wide_strings%b
   --  ada.strings.wide_wide_hash%s
   --  ada.strings.wide_wide_hash%b
   --  ada.tags%s
   --  ada.tags%b
   --  ada.strings.text_buffers%s
   --  ada.strings.text_buffers%b
   --  ada.strings.text_buffers.utils%s
   --  ada.strings.text_buffers.utils%b
   --  ada.wide_wide_characters.handling%s
   --  ada.wide_wide_characters.handling%b
   --  gnat%s
   --  gnat.case_util%s
   --  gnat.debug_utilities%s
   --  gnat.debug_utilities%b
   --  gnat.heap_sort%s
   --  gnat.heap_sort%b
   --  gnat.htable%s
   --  gnat.htable%b
   --  gnat.io%s
   --  gnat.io%b
   --  gnat.os_lib%s
   --  gnat.source_info%s
   --  gnat.string_hash%s
   --  gnat.strings%s
   --  interfaces.c.extensions%s
   --  interfaces.c.strings%s
   --  interfaces.c.strings%b
   --  ada.environment_variables%s
   --  ada.environment_variables%b
   --  system.arith_32%s
   --  system.arith_32%b
   --  system.arith_64%s
   --  system.arith_64%b
   --  system.atomic_counters%s
   --  system.atomic_counters%b
   --  system.fat_flt%s
   --  system.fat_lflt%s
   --  system.fat_llf%s
   --  system.os_constants%s
   --  system.put_images%s
   --  system.put_images%b
   --  ada.streams%s
   --  ada.streams%b
   --  system.file_control_block%s
   --  system.finalization_root%s
   --  system.finalization_root%b
   --  ada.finalization%s
   --  ada.containers.helpers%s
   --  ada.containers.helpers%b
   --  ada.containers.hash_tables%s
   --  ada.containers.red_black_trees%s
   --  system.file_io%s
   --  system.file_io%b
   --  system.regpat%s
   --  system.regpat%b
   --  gnat.regpat%s
   --  system.storage_pools%s
   --  system.storage_pools%b
   --  system.finalization_masters%s
   --  system.finalization_masters%b
   --  system.storage_pools.subpools%s
   --  system.storage_pools.subpools.finalization%s
   --  system.storage_pools.subpools.finalization%b
   --  system.storage_pools.subpools%b
   --  system.stream_attributes%s
   --  system.stream_attributes.xdr%s
   --  system.stream_attributes.xdr%b
   --  system.stream_attributes%b
   --  ada.strings.unbounded%s
   --  ada.strings.unbounded%b
   --  ada.strings.unbounded.hash%s
   --  ada.strings.unbounded.hash%b
   --  ada.strings.wide_wide_maps%s
   --  ada.strings.wide_wide_maps%b
   --  ada.strings.wide_wide_search%s
   --  ada.strings.wide_wide_search%b
   --  ada.strings.wide_wide_fixed%s
   --  ada.strings.wide_wide_fixed%b
   --  ada.strings.wide_wide_unbounded%s
   --  ada.strings.wide_wide_unbounded%b
   --  ada.strings.wide_wide_unbounded.wide_wide_hash%s
   --  ada.strings.wide_wide_unbounded.wide_wide_hash%b
   --  system.val_enum_8%s
   --  system.val_fixed_64%s
   --  system.wch_wts%s
   --  system.wch_wts%b
   --  ada.calendar%s
   --  ada.calendar%b
   --  ada.calendar.delays%s
   --  ada.calendar.delays%b
   --  ada.calendar.time_zones%s
   --  ada.calendar.time_zones%b
   --  ada.calendar.formatting%s
   --  ada.calendar.formatting%b
   --  ada.text_io%s
   --  ada.text_io%b
   --  gnat.byte_order_mark%s
   --  gnat.byte_order_mark%b
   --  gnat.calendar%s
   --  gnat.calendar%b
   --  gnat.directory_operations%s
   --  gnat.directory_operations%b
   --  gnat.traceback%s
   --  gnat.traceback%b
   --  gnat.traceback.symbolic%s
   --  system.assertions%s
   --  system.assertions%b
   --  system.checked_pools%s
   --  system.exn_int%s
   --  system.exn_lli%s
   --  system.file_attributes%s
   --  system.img_util%s
   --  system.img_util%b
   --  system.img_fixed_32%s
   --  system.img_fixed_64%s
   --  system.pool_global%s
   --  system.pool_global%b
   --  gnat.expect%s
   --  gnat.expect%b
   --  system.random_seed%s
   --  system.random_seed%b
   --  system.random_numbers%s
   --  system.random_numbers%b
   --  system.regexp%s
   --  system.regexp%b
   --  ada.directories%s
   --  ada.directories.hierarchical_file_names%s
   --  ada.directories.validity%s
   --  ada.directories.validity%b
   --  ada.directories%b
   --  ada.directories.hierarchical_file_names%b
   --  system.strings.stream_ops%s
   --  system.strings.stream_ops%b
   --  system.wid_llu%s
   --  system.img_lli%s
   --  system.img_llu%s
   --  gnat.calendar.time_io%s
   --  gnat.calendar.time_io%b
   --  gnat.debug_pools%s
   --  gnat.debug_pools%b
   --  gnatcoll%s
   --  gnatcoll.gmp%s
   --  gnatcoll.gmp.lib%s
   --  gnatcoll.gmp.integers%s
   --  gnatcoll.gmp.integers%b
   --  gnatcoll.storage_pools%s
   --  langkit_support%s
   --  langkit_support.errors%s
   --  adasat%s
   --  adasat%b
   --  adasat.decisions%s
   --  adasat.decisions%b
   --  adasat.vectors%s
   --  adasat.vectors%b
   --  adasat.formulas%s
   --  adasat.formulas%b
   --  adasat.internals%s
   --  adasat.builders%s
   --  adasat.builders%b
   --  adasat.theory%s
   --  adasat.dpll%s
   --  adasat.dpll%b
   --  gnatcoll.atomic%s
   --  gnatcoll.atomic%b
   --  gnatcoll.memory%s
   --  gnatcoll.memory%b
   --  gnatcoll.os%s
   --  gnatcoll.storage_pools.headers%s
   --  gnatcoll.storage_pools.headers%b
   --  gnatcoll.refcount%s
   --  gnatcoll.refcount%b
   --  gnatcoll.string_builders%s
   --  gnatcoll.string_builders%b
   --  gnatcoll.strings_impl%s
   --  gnatcoll.strings_impl%b
   --  gnatcoll.strings%s
   --  gnatcoll.strings%b
   --  gnatcoll.mmap%s
   --  gnatcoll.mmap.system%s
   --  gnatcoll.mmap.system%b
   --  gnatcoll.mmap%b
   --  gnatcoll.templates%s
   --  gnatcoll.templates%b
   --  gnatcoll.terminal%s
   --  gnatcoll.terminal%b
   --  gnatcoll.utils%s
   --  gnatcoll.utils%b
   --  gnatcoll.vfs_types%s
   --  gnatcoll.io%s
   --  gnatcoll.io%b
   --  gnatcoll.path%s
   --  gnatcoll.path%b
   --  gnatcoll.io.native%s
   --  gnatcoll.io.native%b
   --  gnatcoll.remote%s
   --  gnatcoll.remote.db%s
   --  gnatcoll.remote.db%b
   --  gnatcoll.io.remote%s
   --  gnatcoll.io.remote.unix%s
   --  gnatcoll.io.remote.unix%b
   --  gnatcoll.io.remote.windows%s
   --  gnatcoll.io.remote.windows%b
   --  gnatcoll.io.remote%b
   --  gnatcoll.vfs%s
   --  gnatcoll.vfs%b
   --  gnatcoll.traces%s
   --  gnatcoll.traces%b
   --  gnatcoll.iconv%s
   --  gnatcoll.iconv%b
   --  langkit_support.adalog%s
   --  langkit_support.adalog.debug%s
   --  langkit_support.adalog.debug%b
   --  langkit_support.adalog.logic_var%s
   --  langkit_support.adalog.logic_var%b
   --  langkit_support.adalog.solver_interface%s
   --  langkit_support.adalog.solver_interface%b
   --  langkit_support.array_utils%s
   --  langkit_support.array_utils%b
   --  langkit_support.boxes%s
   --  langkit_support.boxes%b
   --  langkit_support.hashes%s
   --  langkit_support.hashes%b
   --  langkit_support.images%s
   --  langkit_support.images%b
   --  langkit_support.iterators%s
   --  langkit_support.iterators%b
   --  langkit_support.packrat%s
   --  langkit_support.packrat%b
   --  langkit_support.relative_get%s
   --  langkit_support.relative_get%b
   --  langkit_support.text%s
   --  langkit_support.text%b
   --  langkit_support.names%s
   --  langkit_support.names%b
   --  langkit_support.names.maps%s
   --  langkit_support.names.maps%b
   --  langkit_support.slocs%s
   --  langkit_support.slocs%b
   --  langkit_support.diagnostics%s
   --  langkit_support.diagnostics%b
   --  langkit_support.diagnostics.output%s
   --  langkit_support.diagnostics.output%b
   --  langkit_support.file_readers%s
   --  langkit_support.file_readers%b
   --  langkit_support.types%s
   --  langkit_support.vectors%s
   --  langkit_support.vectors%b
   --  langkit_support.adalog.solver%s
   --  langkit_support.adalog.solver%b
   --  langkit_support.adalog.generic_main_support%s
   --  langkit_support.adalog.generic_main_support%b
   --  langkit_support.adalog.main_support%s
   --  langkit_support.adalog.main_support%b
   --  langkit_support.cheap_sets%s
   --  langkit_support.cheap_sets%b
   --  langkit_support.generic_bump_ptr%s
   --  langkit_support.generic_bump_ptr%b
   --  langkit_support.bump_ptr%s
   --  langkit_support.bump_ptr%b
   --  langkit_support.bump_ptr_vectors%s
   --  langkit_support.bump_ptr_vectors%b
   --  langkit_support.lexical_envs%s
   --  langkit_support.symbols%s
   --  langkit_support.symbols%b
   --  langkit_support.lexical_envs_impl%s
   --  langkit_support.lexical_envs_impl%b
   --  langkit_support.symbols.precomputed%s
   --  langkit_support.symbols.precomputed%b
   --  langkit_support.token_data_handlers%s
   --  langkit_support.token_data_handlers%b
   --  langkit_support.generic_api%s
   --  langkit_support.internal%s
   --  langkit_support.internal.analysis%s
   --  langkit_support.generic_api.analysis%s
   --  langkit_support.generic_api.introspection%s
   --  langkit_support.internal.conversions%s
   --  langkit_support.internal.introspection%s
   --  langkit_support.internal.descriptor%s
   --  langkit_support.generic_api%b
   --  langkit_support.generic_api.analysis%b
   --  langkit_support.generic_api.introspection%b
   --  langkit_support.internal.analysis%b
   --  langkit_support.internal.introspection%b
   --  langkit_support.tree_traversal_iterator%s
   --  langkit_support.tree_traversal_iterator%b
   --  END ELABORATION ORDER

end langkit_supportmain;
