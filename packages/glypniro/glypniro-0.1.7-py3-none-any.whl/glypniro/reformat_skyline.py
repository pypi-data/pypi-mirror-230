import re
import pandas as pd
import pathlib
import click

glycan_column = "Glycans\nNHFAGNa"
peptide_column = "Peptide\n< ProteinMetrics Confidential >"
scan_number_regex = re.compile(r"id=(\d+)")
replicate_regex = re.compile(r"(\w+)(\d+)$")


@click.command()
@click.option("-b", type=click.Path(exists=True), help="Filepath to Byonic output xlsx file.")
@click.option("-s", type=click.Path(exists=True), help="Filepath to Skyline peptide output in xlsx format")
@click.option("-o", type=click.Path(), help="Filepath to output folder")
def main(b, s, o):
    work = []
    df = pd.read_csv(s)
    byonic = pd.read_excel(b, sheet_name="Spectra")
    split_data = df["Peptide"].str.split("_", expand=True)
    df[peptide_column] = split_data[0]
    df[glycan_column] = split_data[1]
    df["z"] = split_data[2]
    print(df["Glycans\nNHFAGNa"])
    byonic.drop([glycan_column, "z"], axis=1, inplace=True)
    df = df.merge(byonic, on=peptide_column)

    current_condition = ""
    current_replicate = ""
    # df["Replicate"] = df["Replicate"].astype(str)
    matches = df["Replicate"].str.extractall(replicate_regex).reset_index()
    # scan_number = df["Scan #"].str.extractall(scan_number_regex).reset_index()
    df["Condition id"] = matches[0]
    df["Replicate id"] = matches[1]
    df["Area"] = df["Normalized Area"]
    output_folder = o
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    for g, d in df.groupby(["Condition id", "Replicate id"]):
        pd_file = str(pathlib.Path(output_folder).joinpath("_".join(g) + ".txt"))
        byonic_file = str(pathlib.Path(output_folder).joinpath("_".join(g) + ".xlsx"))
        scan_pd = []
        scan_byonic = []
        for i in range(d.shape[0]):
            scan_pd.append(str(i))
            scan_byonic.append("id=" + str(i))
        with pd.ExcelWriter(byonic_file) as writer:
            d["Scan #"] = pd.Series(scan_byonic, index=d.index)
            d["First Scan"] = pd.Series(scan_pd, index=d.index)

            new_df = d[["Protein Name", "Glycans\nNHFAGNa", "Peptide\n< ProteinMetrics Confidential >", "Score", "Scan #",
               "Starting\nposition", "Calc.\nmass (M+H)"]]
            new_df.to_excel(writer, sheet_name="Spectra", index=False)

            new_df = d[["First Scan", "Area"]]
            new_df.to_csv(pd_file, sep="\t", index=False)

            work.append([g[0], g[1], byonic_file, pd_file])

    work = pd.DataFrame(work, columns=["condition_id", "replicate_id", "filename", "area_filename"])
    with pd.ExcelWriter(str(pathlib.Path(output_folder).joinpath("work.xlsx"))) as writer:
        work.to_excel(writer, index=False)

