from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView

import pandas as pd
from rest_framework.response import Response
from django.conf import settings as GLOBAL_SETTINGS
from rest_framework.exceptions import NotAcceptable

from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
)
from .utils import authorize_request, querydict_to_dict


class VCFMixIn(object):

    def __init__(self):
        self.vcf_file_path = GLOBAL_SETTINGS.VCF_FILE_PATH
        self.pagination_page = 1
        self.pagination_size = 30
        self.id_filter = None
        self.number_of_commented_lines = 0  # Number of commented from the beginning of the file

    def set_pagination_parameters(self, pagination_size, pagination_page):
        self.pagination_size = pagination_size or self.pagination_size
        self.pagination_page = pagination_page or self.pagination_page

    def set_filters(self, id):
        self.id_filter = id

    def get_vcf_names(self):
        # with gzip.open(self.vcf_file_path, "rt") as ifile
        with open(self.vcf_file_path, "rt") as ifile:
            for line_number, line in enumerate(ifile):
                if line.startswith("#CHROM"):
                    self.number_of_commented_lines = line_number
                    vcf_names = [x for x in line.split('\t')]
                    break
        ifile.close()
        return vcf_names

    def get_data(self, columns=['#CHROM', 'POS', 'ID', 'REF', 'ALT'], column_renames={'#CHROM': 'CHROM'}, get_all=False):
        names = self.get_vcf_names()
        vcf = pd.read_csv(self.vcf_file_path, comment='#', delim_whitespace=True, index_col=False, header=None, names=names)
        vcf = vcf[columns].rename(columns=column_renames)
        ps = (self.pagination_page-1)*self.pagination_size
        pe = ps + self.pagination_size
        if self.id_filter:
            vcf = vcf.loc[vcf['ID'] == self.id_filter]
        return vcf if get_all else vcf[ps:pe]

    def update_records(self, df_rows, data):
        for item in data.items():
            df_rows[item[0]] = item[1]
            df_index_list = df_rows.index.values.tolist()
        lines = []
        with open(self.vcf_file_path, 'r') as fp:
            lines = fp.readlines()

        with open(self.vcf_file_path, 'w') as fp:
            for number, line in enumerate(lines):
                if number not in [df_index + self.number_of_commented_lines + 1 for df_index in df_index_list]:
                    fp.write(line)
                else:
                    fp.write("{CHROM}\t{POS}\t{ID}\t{REF}\t{ALT}\t\n".format(**df_rows.loc[number - self.number_of_commented_lines - 1]))


    def delete_records(self, df_index_list):
        lines = []
        with open(self.vcf_file_path, 'r') as fp:
            lines = fp.readlines()

        with open(self.vcf_file_path, 'w') as fp:
            for number, line in enumerate(lines):
                if number not in [df_index + self.number_of_commented_lines + 1 for df_index in df_index_list]:
                    fp.write(line)

    def get_data_in_json_format(self):
        return self.get_data().to_json(orient='index')

    def get_data_in_xml_format(self):
        return self.get_data().to_xml()


class GetDataAPIView(VCFMixIn, ListAPIView):

    def get(self, request):
        accept_http_header = request.META.get('HTTP_ACCEPT', None)
        self.set_filters(request.GET.get('id', None))
        self.set_pagination_parameters(int(request.GET.get('pagination-size')), int(request.GET.get('pagination-page')))
        if accept_http_header in ['application/json', '*/*', None]:
            data = self.get_data_in_json_format()
        elif accept_http_header == 'application/xml':
            data = self.get_data_in_xml_format()
        else:
            raise NotAcceptable
        return Response(data=data, status=HTTP_200_OK)


class AppendDataAPIView(VCFMixIn, CreateAPIView):

    def post(self, request):
        authorize_request(request.headers.get('Authorization'))
        data = querydict_to_dict(request.POST)
        with open(self.vcf_file_path, "a") as file_object:
            # Append at the end of the file
            file_object.write("{CHROM}\t{POS}\t{ID}\t{REF}\t{ALT}\t\n".format(**data))
        return Response(status=HTTP_201_CREATED)


class UpdateDataAPIView(VCFMixIn, UpdateAPIView):

    def put(self, request):
        authorize_request(request.headers.get('Authorization'))
        data_id = request.POST.get('ID', None)
        if data_id:
            self.set_filters(data_id)
            df_rows = self.get_data(get_all=True)
            if not df_rows.empty:
                self.update_records(df_rows, querydict_to_dict(request.POST))
                status = HTTP_200_OK
            else:
                status = HTTP_404_NOT_FOUND
        else:
            status = HTTP_400_BAD_REQUEST
        return Response(status=status)

class DeleteDataAPIView(VCFMixIn, DestroyAPIView):

    def delete(self, request):
        authorize_request(request.headers.get('Authorization'))
        data_id = request.POST.get('ID', None)
        if data_id:
            self.set_filters(data_id)
            df_index_list = self.get_data(get_all=True).index.values.tolist()
            if df_index_list:
                self.delete_records(df_index_list)
                status = HTTP_204_NO_CONTENT
            else:
                status = HTTP_404_NOT_FOUND
        else:
            status = HTTP_400_BAD_REQUEST
        return Response(status=status)
