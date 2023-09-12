import pandas as pd
from glypniro.common import GlypnirO, process_tmt_pd_byonic, GlypnirOComponent, filter_with_U, \
    add_custom_glycan_categories

import click


@click.command()
@click.option("--input-file", "-i", help="Filepath to experiment description file where each row has 4 columns, condition_id, replicate_id, filename, and area_filename", type=click.Path(exists=True))
@click.option("--output", "-o", help="Filepath to output", type=click.Path(exists=False))
@click.option("--score-cutoff", "-s", help="Filter the data by specific Byonic cut-off quality score", type=float, default=200)
@click.option("--trust-byonic", "-t", help="Enable site specific glycan position parsing from Byonic", is_flag=True)
@click.option("--get-uniprot", "-g", help="Required internet connection. Enable parsing of UniProt ID from protein name and request the original protein name from the UniProt databas.", is_flag=True)
@click.option("--parse-uniprot", "-p", help="Attempt to parse UniProt ID from protein name", is_flag=True)
@click.option("--debug", "-d", help="In conjunction to the final output, the script would also create debug files that contain the "
                         "unique PSM selected for calculation of the data in the final output", is_flag=True)
@click.option("--mode", "-m", help="Select the mode of operation. 0: Byonic only, 1: PD only, 2: Byonic and PD", type=int, default=1)
@click.option("--custom-group", "-c", help="A tabulated text file with two columns, Glycans and Labels. Glycans must be the glycans appear in the result and labels is the custome label for them", type=click.Path(exists=True))
def main(input_file, output, score_cutoff, trust_byonic, get_uniprot, parse_uniprot, debug, mode, custom_group):
    """
    Automated workflow for processing and combining Byonic and PD output
    """
    print(input_file, output, score_cutoff, trust_byonic, get_uniprot, parse_uniprot, debug, mode, custom_group)
    ex = GlypnirO(trust_byonic=trust_byonic, get_uniprot=get_uniprot, debug=debug,
                  parse_uniprot=parse_uniprot)
    if mode == 1:
        for i, r in ex.add_batch_component(input_file, score_cutoff):
            print(r)
        ex.process_components()
        result = ex.analyze_components(relabel=custom_group)
        if trust_byonic:
            if custom_group:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Glycosylated positions in "
                                  "peptide", "Categories",
                                  "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Glycosylated positions in peptide", "Categories"]
            else:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Glycosylated positions in "
                                  "peptide",
                                  "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Glycosylated positions in peptide"]
        else:
            if custom_group:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Position peptide N-terminus", "Peptides", "Labels", "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Position peptide N-terminus", "Peptides", "Labels"]
            else:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Position peptide N-terminus", "Peptides", "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Position peptide N-terminus", "Peptides"]
        with pd.ExcelWriter(output) as writer:
            print("Writing Occupancy data to excel sheets.")
            if not result["Occupancy"].empty:
                result["Occupancy"].to_excel(writer, sheet_name="Unglyco_and_Glycoforms_Prop")
            if not result["Occupancy_Without_Proportion_U"].empty:
                result["Occupancy_Without_Proportion_U"].to_excel(writer, sheet_name="Unglyco_and_Glycoforms_Sep")
            if not result["Occupancy_With_U"].empty:
                result["Occupancy_With_U"].to_excel(writer, sheet_name="Unglycosylated")
            if not result["Glycoforms"].empty:
                result["Glycoforms"].to_excel(writer, sheet_name="Glycoforms")
        if custom_group:
            with pd.ExcelWriter(output + "glycan_grouped.xlsx") as writer:
                if not result["Occupancy"].empty:
                    result["Occupancy"].groupby(grouping_array[:-1]).sum().to_excel(writer,
                                                                                    sheet_name="Unglyco_and_Glycoforms_Prop")
                if not result["Occupancy_Without_Proportion_U"].empty:
                    result["Occupancy_Without_Proportion_U"].groupby(grouping_array[:-1]).sum().to_excel(writer,
                                                                                                         sheet_name="Unglyco_and_Glycoforms_Sep")
                if not result["Occupancy_With_U"].empty:
                    result["Occupancy_With_U"].groupby(grouping_array[:-1]).sum().to_excel(writer,
                                                                                           sheet_name="Unglycosylated")
                if not result["Glycoforms"].empty:
                    result["Glycoforms"].groupby(grouping_array[:-1]).sum().to_excel(writer, sheet_name="Glycoforms")

        if ex.debug:
            for u in ex.unique_dict:
                with pd.ExcelWriter(output + "_" + u + ".xlsx") as writer:
                    df = pd.DataFrame(ex.unique_dict[u])
                    df.to_excel(writer, index=False)
    elif mode == 2:
        if input_file.endswith(".txt") or input_file.endswith(".tsv"):
            data = pd.read_csv(input_file, sep="\t", encoding="utf-8")
        elif input_file.endswith(".csv"):
            data = pd.read_csv(input_file, encoding="utf-8")
        elif input_file.endswith(".xlsx"):
            data = pd.read_excel(input_file)
        data, sample_info = process_tmt_pd_byonic(data)

        ex.uniprot_parsed_data = data[["Master Protein Accessions", "Protein Descriptions"]].rename(
            columns={"Master Protein Accessions": "Entry", "Protein Descriptions": "Protein names"})
        component = GlypnirOComponent(data, mode=mode, trust_byonic=trust_byonic)
        component.process(mode=mode, tmt_info=sample_info, protein_column="Master Protein Accessions",
                          sequence_column="Annotated Sequence", glycans_column="Glycan composition",
                          starting_position_column="Position in Protein")

        result = component.analyze(debug=debug, protein_column="Master Protein Accessions",
                                   glycans_column="Glycan composition", starting_position_column="Position in Protein",
                                   mode=mode, tmt_info=sample_info, observed_mz_column="m/z [Da]")
        if debug:
            pd.DataFrame(component.unique_rows).to_csv(output + "_debug.txt", sep="\t", index=False)
        output1 = []
        output_without_u = []
        output_occupancy_no_calculation_u = []

        if not result.empty:
            for s in result.separate_result():
                print(s.df)
                a = s.to_summary(name="Raw", trust_byonic=trust_byonic)

                pro = s.calculate_proportion()
                b = s.to_summary(pro, "Proportion", trust_byonic=trust_byonic)
                condition = "None"
                for cond in sample_info:
                    if s.df.columns[-1] in sample_info[cond]:
                        condition = cond
                temp_df = ex._summary(a, b, add_protein=False, condition=condition, replicate=s.df.columns[-1])
                # print(temp_df)
                output1.append(temp_df)

                # proportion for glycoforms here are calculated without unglycosylated form.
                a_without_u = s.to_summary(name="Raw", trust_byonic=trust_byonic, occupancy=False)
                pro_without_u = s.calculate_proportion(occupancy=False)
                b_without_u = s.to_summary(pro_without_u, "Proportion", trust_byonic=trust_byonic,
                                           occupancy=False)

                temp_df_without_u = ex._summary(a_without_u, b_without_u, add_protein=False, condition=condition,
                                                replicate=s.df.columns[-1])
                output_without_u.append(temp_df_without_u)

                temp_df_no_calculation_u = ex._summary(a, b_without_u, add_protein=False, condition=condition,
                                                       replicate=s.df.columns[-1])
                output_occupancy_no_calculation_u.append(temp_df_no_calculation_u)

        result_occupancy = ex._summary_format(output1, relabeling=custom_group)
        result_occupancy_with_u = ex._summary_format(output1, filter_with_U, True, relabeling=custom_group)
        result_glycoform = ex._summary_format(output_without_u, relabeling=custom_group)
        tempdf_index_reset_result_occupancy_with_u = result_occupancy_with_u.reset_index()
        tempdf_index_reset_result_glycoform = result_glycoform.reset_index()
        print(tempdf_index_reset_result_glycoform)

        result_occupancy_glycoform_sep = pd.concat(
            [tempdf_index_reset_result_glycoform, tempdf_index_reset_result_occupancy_with_u])
        # format the output with the correct column name for site specific or peptide level analysis
        if trust_byonic:
            if custom_group:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Glycosylated positions in "
                                  "peptide", "Categories",
                                  "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Glycosylated positions in peptide", "Categories"]
            else:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Glycosylated positions in "
                                  "peptide",
                                  "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Glycosylated positions in peptide"]
            print(result_occupancy_glycoform_sep)
            result_occupancy_glycoform_sep = result_occupancy_glycoform_sep.set_index(grouping_array)
            result_occupancy_glycoform_sep = result_occupancy_glycoform_sep.sort_index(
                level=sorting_array)
        else:
            if custom_group:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Position peptide N-terminus", "Peptides", "Labels", "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Position peptide N-terminus", "Peptides", "Labels"]
            else:
                grouping_array = ["Protein", "Protein names",
                                  # "Isoform",
                                  "Position peptide N-terminus", "Peptides", "Glycans"]
                sorting_array = ["Protein", "Protein names",
                                 # "Isoform",
                                 "Position peptide N-terminus", "Peptides"]
            result_occupancy_glycoform_sep = result_occupancy_glycoform_sep.set_index(
                grouping_array)
            result_occupancy_glycoform_sep = result_occupancy_glycoform_sep.sort_index(
                level=sorting_array)
        with pd.ExcelWriter(output) as writer:
            print("Writing Occupancy data to excel sheets.")
            if not result_occupancy.empty:
                result_occupancy.to_excel(writer, sheet_name="Unglyco_and_Glycoforms_Prop")
            if not result_occupancy_glycoform_sep.empty:
                result_occupancy_glycoform_sep.to_excel(writer, sheet_name="Unglyco_and_Glycoforms_Sep")
            if not result_occupancy_with_u.empty:
                result_occupancy_with_u.to_excel(writer, sheet_name="Unglycosylated")
            if not result_glycoform.empty:
                result_glycoform.to_excel(writer, sheet_name="Glycoforms")
        if custom_group:
            with pd.ExcelWriter(output + "glycan_grouped.xlsx") as writer:
                if not result_occupancy.empty:
                    result_occupancy.groupby(grouping_array[:-1]).sum().to_excel(writer,
                                                                                 sheet_name="Unglyco_and_Glycoforms_Prop")
                if not result_occupancy_glycoform_sep.empty:
                    result_occupancy_glycoform_sep.groupby(grouping_array[:-1]).sum().to_excel(writer,
                                                                                               sheet_name="Unglyco_and_Glycoforms_Sep")
                if not result_occupancy_with_u.empty:
                    result_occupancy_with_u.groupby(grouping_array[:-1]).sum().to_excel(writer,
                                                                                        sheet_name="Unglycosylated")
                if not result_glycoform.empty:
                    result_glycoform.groupby(grouping_array[:-1]).sum().to_excel(writer, sheet_name="Glycoforms")

    print("Completed.")


